"""Helpers for subscribing to S3 buckets."""
import os
import json
import logging

import boto3
import requests
import csvkit.convert

from sandman import db

from flask.views import MethodView
from flask import request, jsonify, Blueprint

import aws
import tasks
import utils
import config
import signing

logger = logging.getLogger(__name__)

def subscribe(bucket, region='us-east-1'):
    sns = boto3.resource('sns', region)
    client = boto3.client('sns', region)
    topic = get_topic(sns, client)
    policy = get_policy(topic.arn, bucket)
    topic.set_attributes(AttributeName='Policy', AttributeValue=json.dumps(policy))
    notify(topic.arn, bucket)
    client.subscribe(
        TopicArn=topic.arn,
        Protocol='https',
        Endpoint='https://autoapi.18f.gov/webhook/',
    )

def get_topic(sns, client):
    """Get or create SNS topic."""
    topic = next(
        (topic for topic in sns.topics.all() if topic.arn.endswith('autoapi')),
        None,
    )
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
        }
    )

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
            name, ext = os.path.splitext(key['key'])
            if ext.lstrip('.') not in csvkit.convert.SUPPORTED_FORMATS:
                continue
            if record['eventName'].startswith('ObjectCreated'):
                fetch_key(client, bucket['name'], key['key'])
            elif record['eventName'].startswith('ObjectRemoved'):
                utils.drop_table(name, metadata=db.metadata, engine=db.engine)

def fetch_bucket(bucket_name=None):
    bucket_name = bucket_name or config.BUCKET_NAME
    logger.info('Importing bucket {0}'.format(bucket_name))
    aws.subscribe(bucket_name)
    s3 = boto3.resource('s3')
    client = boto3.client('s3')
    bucket = s3.Bucket(bucket_name)
    for key in bucket.objects.all():
        name, ext = os.path.splitext(key.key)
        if ext.lstrip('.') not in csvkit.convert.SUPPORTED_FORMATS:
            continue
        fetch_key(client, bucket.name, key.key)

def fetch_key(client, bucket, key):
    filename = os.path.join('raw', key)
    client.download_file(bucket, key, filename)
    try:
        tasks.apify(filename)
    except Exception as error:
        logger.exception(error)

def make_blueprint():
    blueprint = Blueprint('aws', __name__)
    blueprint.add_url_rule('/webhook/', view_func=AwsWebhookView.as_view('aws_webhook'))
    return blueprint
