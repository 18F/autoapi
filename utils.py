import os
import logging
import tempfile

import sandman2
import sqlalchemy as sa
from flask import json, current_app
from csvkit.utilities.in2csv import In2CSV

import pandas as pd
from pandas.io.sql import SQLTable
from pandas.io.sql import pandasSQL_builder


import config

logger = logging.getLogger(__name__)

def get_name(path):
    return os.path.splitext(os.path.split(path)[1])[0]

class APIJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if hasattr(o, 'isoformat'):
            return o.isoformat()
        return super(APIJSONEncoder, self).default(o)

def to_sql(name, engine, frame, chunksize=None, **kwargs):
    table = SQLTable(name, engine, frame=frame, **kwargs)
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
    converter = In2CSV()
    converter.args.input_path = filename
    converter.output_file = file
    converter.main()
    return file

def load_table(filename, tablename, engine=None, infer_size=100, chunk_size=1000):
    engine = engine or sa.create_engine(config.SQLA_URI)
    file = ensure_csv(filename)
    # Pass data types to iterator to ensure consistent types across chunks
    dtypes = pd.read_csv(file.name, nrows=infer_size).dtypes
    chunks = pd.read_csv(file.name, chunksize=chunk_size, iterator=True, dtype=dtypes)
    for idx, chunk in enumerate(chunks):
        chunk.index += chunk_size * idx
        sql_engine = pandasSQL_builder(engine)
        to_sql(
            tablename, sql_engine, chunk,
            chunksize=chunk_size, keys='index', if_exists='append',
        )

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
    refresh_tables()

def get_tables(engine=None):
    engine = engine or sa.create_engine(config.SQLA_URI)
    inspector = sa.engine.reflection.Inspector.from_engine(sandman2.db.engine)
    return set(inspector.get_table_names())

def refresh_tables():
    sandman2.db.metadata.clear()
    activate()

def activate():
    rules = [
        rule for rule in current_app.url_map._rules
        if is_service_rule(rule, current_app)
    ]
    for rule in rules:
        current_app.url_map._rules.remove(rule)
        current_app.url_map._rules_by_endpoint.pop(rule.endpoint, None)
        current_app.view_functions.pop(rule.endpoint, None)
    sandman2.AutomapModel.classes.clear()
    sandman2.AutomapModel.metadata.clear()
    sandman2._reflect_all()

def is_service_rule(rule, app):
    view = current_app.view_functions[rule.endpoint]
    return hasattr(view, 'view_class') and issubclass(view.view_class, sandman2.Service)
