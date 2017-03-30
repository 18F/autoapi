"""Helpers for subscribing to S3 buckets."""
import json
import logging
import os
import urllib

import boto3
import cfenv
import csvkit.convert
import requests
from flask import Blueprint, jsonify, request
from flask.views import MethodView

import config
import signing
import tasks
import utils
from sandman2.model import db

logger = logging.getLogger(__name__)


def subscribe(bucket, region='us-east-1'):
    sns = boto3.resource('sns', region)
    client = boto3.client('sns', region)
    topic = get_topic(sns, client)
    policy = get_policy(topic.arn, bucket)
    topic.set_attributes(AttributeName='Policy',
                         AttributeValue=json.dumps(policy))
    notify(topic.arn, bucket)
    client.subscribe(
        TopicArn=topic.arn,
        Protocol='https',
        Endpoint=urllib.parse.urljoin(config.BASE_URL, 'webhook/'), )


def get_topic(sns, client):
    """Get or create SNS topic."""
    topic = next(
        (topic for topic in sns.topics.all() if topic.arn.endswith('autoapi')),
        None, )
    if topic is None:
        response = client.create_topic(Name='autoapi')
        topic = sns.Topic(response['TopicArn'])
        topic.reload()
    return topic


def notify(arn, bucket):
    client = boto3.client('s3', 'us-east-1')
    client.put_bucket_notification_configuration(
        Bucket=bucket,
        NotificationConfiguration={
            'TopicConfigurations': [
                {
                    'TopicArn': arn,
                    'Events': ['s3:ObjectCreated:*', 's3:ObjectRemoved:*'],
                }
            ]
        })


def get_policy(arn, bucket):
    return {
        'Statement': [
            {
                'Effect': 'Allow',
                'Principal': {'AWS': '*'},
                'Action': ['SNS:Publish'],
                'Resource': arn,
            }
        ]
    }


class AwsWebhookView(MethodView):
    def post(self):
        data = json.loads(request.data.decode('utf-8'))
        logger.info('Received hook with data {0}'.format(data))
        signing.verify(data)
        if data['Type'] == 'SubscriptionConfirmation':
            self.handle_subscribe(data)
        elif data['Type'] == 'Notification':
            self.handle_notification(data)
        return jsonify({'status': 'success'})

    def handle_subscribe(self, data):
        requests.get(data['SubscribeURL'])

    def handle_notification(self, data):
        client = boto3.client('s3')
        message = json.loads(data['Message'])
        for record in message.get('Records', []):
            bucket = record['s3']['bucket']
            key = record['s3']['object']
            path = urllib.parse.unquote_plus(key['key'])
            name, ext = os.path.splitext(path)
            name = name.replace('/', '-')
            if ext.lstrip('.') not in csvkit.convert.SUPPORTED_FORMATS:
                continue
            if record['eventName'].startswith('ObjectCreated'):
                fetch_key(client, bucket['name'], path)
            elif record['eventName'].startswith('ObjectRemoved'):
                utils.drop_table(name, metadata=db.metadata, engine=db.engine)


def cf_bucket():
    env = cfenv.AppEnv()
    if env.app:
        try:
            session = boto3.Session(
                region_name=env.get_credential('region'),
                aws_access_key_id=env.get_credential('access_key_id'),
                aws_secret_access_key=env.get_credential(
                    'secret_access_key'), )
            s3 = session.resource('s3')
            client = session.client('s3')
            return (client, s3.Bucket(env.get_credential('bucket')))
        except Exception as e:
            logger.error(e)
    return (None, None)


def _get_bucket(bucket_name=None):
    '''
    Return a tuple containing a Boto3 S3 client and a Boto3
    S3 bucket.
    '''

    (client, bucket) = cf_bucket()
    if bucket:
        logger.info('Using bound bucket {0}'.format(bucket))
        logger.info('bucket name {0}'.format(bucket.name))
        # aws.subscribe(bucket.name)
    else:
        bucket_name = bucket_name or config.BUCKET_NAME
        logger.info('Importing bucket {0}'.format(bucket_name))
        # aws.subscribe(bucket_name) lacking permissions
        s3 = boto3.resource('s3')
        client = boto3.client('s3')
        bucket = s3.Bucket(bucket_name)

    return (client, bucket)


def delete_from_bucket(filename, bucket_name=None):
    (client, bucket) = _get_bucket(bucket_name)

    bucket.delete_objects(
        Delete={
            'Objects': [
                {'Key': filename}
            ]
        }
    )

    logger.info('deleted {}.'.format(filename))


def copy_to_bucket(filename, bucket_name=None):
    (client, bucket) = _get_bucket(bucket_name)

    keyname = os.path.basename(filename)

    with open(filename, 'rb') as f:
        bucket.put_object(
            Body=f,
            Key=keyname
        )

    logger.info('uploaded {}.'.format(keyname))


def list_bucket(bucket_name=None):
    (client, bucket) = _get_bucket(bucket_name)

    for key in bucket.objects.all():
        print(key.key)


def fetch_bucket(bucket_name=None, clear_tables=True):
    '''
    Download the CSV files in the given bucket and add their
    data to the database, optionally clearing the relevant
    database tables first.
    '''

    (client, bucket) = _get_bucket(bucket_name)

    if clear_tables:
        utils.clear_tables()

    for key in bucket.objects.all():
        name, ext = os.path.splitext(key.key)
        logger.info('object found in bucket: {}.{}'.format(name, ext))
        if ext.lstrip('.') not in csvkit.convert.SUPPORTED_FORMATS:
            continue
        fetch_key(client, bucket.name, key.key)


def fetch_key(client, bucket, key):
    logger.info('fetching key {} from AWS'.format(key))
    dirname = 'raw'
    filename = os.path.join(dirname, key.replace('/', '-'))

    if not os.path.exists(dirname):
        os.mkdir(dirname)

    client.download_file(bucket, key, filename)
    logger.info('Downloaded {}'.format(filename))
    try:
        tasks.apify(filename)
    except Exception as error:
        logger.exception(error)


def make_blueprint():
    blueprint = Blueprint('aws', __name__)
    blueprint.add_url_rule('/webhook/',
                           view_func=AwsWebhookView.as_view('aws_webhook'))
    return blueprint
