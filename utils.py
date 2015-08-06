import os

from flask import json
import sqlalchemy as sa

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

def activate(base=ReadOnlyModel, browser=False, admin=False, **kwargs):
    sandman_activate(base=base, browser=browser, admin=admin, **kwargs)

def drop_table(tablename, metadata=None, engine=None):
    metadata = metadata or sa.MetaData()
    engine = engine or sa.create_engine(config.SQLA_URI)
    try:
        table = sa.Table(tablename, metadata, autoload_with=engine)
        table.drop(engine)
    except sa.exc.NoSuchTableError:
        pass
    refresh_tables()

def refresh_tables():
    db.metadata.clear()
    activate(base=ReadOnlyModel, reflect_all=True, browser=False, admin=False)
