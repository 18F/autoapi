import logging

import sqlalchemy as sa
from invoke import run, task

import app
import aws
import config
import refresh_log
import utils
from refresh_log import AutoapiTableRefreshLog as RefreshLog

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
    try:
        utils.drop_table(tablename)
    except sa.exc.OperationalError as e:
        logger.warning('DROP TABLE {} failed, may not exist?'.format(
            tablename))
        logger.warning(str(e))
    utils.load_table(filename, tablename)
    utils.index_table(tablename, config.CASE_INSENSITIVE)
    logger.info('Finished importing {0}'.format(filename))


@task
def fetch_bucket(bucket_name=None):
    aws.fetch_bucket(bucket_name)


@task
def serve():
    app.make_app().run(host='0.0.0.0')


@task
def refresh():
    logger.info('Refresh invoked')
    with app.make_app().app_context():
        rlog_id = RefreshLog.start()
        logger.info('refresh log id {} started'.format(rlog_id))
        try:
            aws.fetch_bucket()
            logger.debug('bucket fetched')
            utils.refresh_tables()
            logger.info('refresh complete')
            refresh_log.stop(rlog_id)
        except Exception as e:
            refresh_log.stop(rlog_id, err_msg=str(e))


@task
def clear():
    utils.clear_tables()
