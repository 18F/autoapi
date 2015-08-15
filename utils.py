import os

from flask import json
import sqlalchemy as sa

import pandas as pd
from pandas.io.sql import SQLTable
from pandas.io.sql import pandasSQL_builder

from sandman import db
from sandman.model.models import Model
from sandman.model import activate as sandman_activate

import config

def get_name(path):
    return os.path.splitext(os.path.split(path)[1])[0]

class ReadOnlyModel(Model):
    __methods__ = ('GET', )

class APIJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if hasattr(o, 'isoformat'):
            return o.isoformat()
        return super(APIJSONEncoder, self).default(o)

def activate(*args, base=ReadOnlyModel, browser=False, admin=False, reflect_all=True):
    sandman_activate(base=base, browser=browser, admin=admin, reflect_all=reflect_all)

def to_sql(name, engine, frame, chunksize=None, **kwargs):
    table = SQLTable(name, engine, frame=frame, **kwargs)
    table.create()
    table.insert(chunksize)

def load_table(filename, tablename, engine=None, infer_size=100, chunk_size=1000):
    engine = engine or sa.create_engine(config.SQLA_URI)
    dtypes = pd.read_csv(filename, nrows=infer_size).dtypes
    chunks = pd.read_csv(filename, chunksize=chunk_size, iterator=True, dtype=dtypes)
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
            except sa.exc.OperationalError:
                pass
            try:
                index.create(engine)
            except sa.exc.OperationalError:
                pass

def drop_table(tablename, metadata=None, engine=None):
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
    inspector = sa.engine.reflection.Inspector.from_engine(db.engine)
    return set(inspector.get_table_names())

def refresh_tables():
    db.metadata.clear()
    activate()
