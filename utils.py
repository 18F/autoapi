import logging
import os
import tempfile

import pandas as pd
import sqlalchemy as sa
from csvkit.utilities.in2csv import In2CSV
from flask import current_app, json
from pandas.io.sql import SQLTable, pandasSQL_builder
from sqlalchemy.ext.automap import automap_base

import config
import sandman2
import swagger
from refresh_log import AutoapiTableRefreshLog
from sandman2 import model

logger = logging.getLogger(__name__)


def get_name(path):
    return os.path.splitext(os.path.split(path)[1])[0]


class APIJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if hasattr(o, 'isoformat'):
            return o.isoformat()
        return super(APIJSONEncoder, self).default(o)


class Base(model.Model):
    __methods__ = {'GET'}


AutomapModel = automap_base(cls=(Base, model.db.Model))


def to_sql(name, engine, frame, chunksize=None, **kwargs):
    pandas_sql_engine = pandasSQL_builder(engine)
    table = SQLTable(name, pandas_sql_engine, frame=frame, **kwargs)
    table.create()
    table.insert(chunksize)


def ensure_csv(filename):
    """Ensure that `filename` is a CSV.

    :param filename: Name of tabular file
    :returns: File pointer to original or converted file
    """
    _, ext = os.path.splitext(filename)
    if ext == '.csv':
        return open(filename)
    logger.info('Converting file {0} to CSV'.format(filename))
    file = tempfile.NamedTemporaryFile('w')
    converter = In2CSV((filename, ))
    converter.args.input_path = filename
    converter.output_file = file
    converter.main()
    return file


def clear_tables(metadata=None, engine=None):
    metadata = metadata or sa.MetaData()
    if not metadata.bind:
        metadata.bind = engine or sa.create_engine(config.SQLA_URI)
    metadata.reflect()
    clearable = [m[1]
                 for m in metadata.tables.items()
                 if m[0] != AutoapiTableRefreshLog.__tablename__]
    logger.debug('{} clearable tables:'.format(len(clearable)))
    logger.debug(str([t.name for t in clearable]))
    try:
        metadata.drop_all(tables=clearable)
    except Exception as e:
        logger.info('drop error: {}'.format(str(e)))
    logger.info('all clearables dropped')


def load_table(filename,
               tablename,
               engine=None,
               infer_size=100,
               chunksize=1000):
    engine = engine or sa.create_engine(config.SQLA_URI)
    file = ensure_csv(filename)
    # Pass data types to iterator to ensure consistent types across chunks
    dtypes = pd.read_csv(file.name, nrows=infer_size,
                         skipinitialspace=True).dtypes
    chunks = pd.read_csv(file.name,
                         iterator=True,
                         chunksize=chunksize,
                         dtype=dtypes,
                         skipinitialspace=True)
    for idx, chunk in enumerate(chunks):
        chunk.index += chunksize * idx
        to_sql(tablename,
               engine,
               chunk,
               chunksize=chunksize,
               keys='index',
               if_exists='append', )


def index_table(tablename, case_insensitive=False, metadata=None, engine=None):
    """Index all columns on `tablename`, optionally using case-insensitive
    indexes on string columns when supported by the database.
    """
    metadata = metadata or sa.MetaData()
    engine = engine or sa.create_engine(config.SQLA_URI)
    table = sa.Table(tablename, metadata, autoload_with=engine)
    for label, column in table.columns.items():
        if label == 'index':
            continue
        index_name = 'ix_{0}'.format(label.lower())
        indexes = [sa.Index(index_name, column)]
        if case_insensitive:
            indexes.insert(0, sa.Index(index_name, sa.func.upper(column)))
        for index in indexes:
            try:
                index.drop(engine)
            except sa.exc.DatabaseError:
                pass
            try:
                index.create(engine)
            except sa.exc.DatabaseError:
                pass


def drop_table(tablename, metadata=None, engine=None):
    logger.info('Dropping table {0}'.format(tablename))
    metadata = metadata or sa.MetaData()
    engine = engine or sa.create_engine(config.SQLA_URI)
    try:
        table = sa.Table(tablename, metadata, autoload_with=engine)
        table.drop(engine)
    except sa.exc.NoSuchTableError:
        pass


def get_tables(engine=None):
    engine = engine or sa.create_engine(config.SQLA_URI)
    inspector = sa.engine.reflection.Inspector.from_engine(sandman2.db.engine)
    return set(inspector.get_table_names())


def refresh_tables():
    sandman2.db.metadata.clear()
    activate()


def activate():
    with current_app.app_context():
        rules = [
            rule
            for rule in current_app.url_map._rules
            if is_service_rule(rule, current_app)
        ]
        for rule in rules:
            current_app.url_map._rules.remove(rule)
            current_app.url_map._rules_by_endpoint.pop(rule.endpoint, None)
            current_app.view_functions.pop(rule.endpoint, None)
        sandman2.AutomapModel.classes.clear()
        sandman2.AutomapModel.metadata.clear()
        sandman2._reflect_all(Base=AutomapModel)
        tables = get_tables()
        sandman2.unregister_services(to_keep=tables)
        current_app.__spec__ = swagger.make_spec(current_app)
        current_app.config['SQLALCHEMY_TABLES'] = tables


def is_service_rule(rule, app):
    view = current_app.view_functions[rule.endpoint]
    return hasattr(view, 'view_class') and issubclass(view.view_class,
                                                      sandman2.Service)
