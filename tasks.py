import logging

from invoke import task, run

import aws
import utils
import config

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

@task
def requirements(upgrade=True):
    cmd = 'pip install -r requirements.txt'
    if upgrade:
        cmd += ' --upgrade'
    run(cmd)

@task
def apify(filename, tablename=None):
    tablename = tablename or utils.get_name(filename)
    logger.info('Importing {0} to table {1}'.format(filename, tablename))
    utils.drop_table(tablename)
    utils.load_table(filename, tablename)
    utils.index_table(tablename, config.CASE_INSENSITIVE)
    logger.info('Finished importing {0}'.format(filename))

@task
def fetch_bucket(bucket_name=None):
    aws.fetch_bucket(bucket_name)
