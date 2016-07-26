import config
from app import make_app

import pytest
from sqlalchemy import create_engine, MetaData


@pytest.yield_fixture
def app():
    create_db(config.SQLA_URI)
    autoapi_app = make_app()
    yield autoapi_app
    drop_db(config.SQLA_URI)


def create_db(sqlalchemy_uri):
    CREATE_TABLE_SQL = """
        CREATE TABLE people (
            id int primary key,
            name text,
            dob date,
            number_of_pets int)
    """
    INSERT_TABLE_SQL = """
        INSERT INTO people (id, name, dob, number_of_pets)
        VALUES (?, ?, ?, ?)
    """
    engine = create_engine(config.SQLA_URI)
    connection = engine.connect()
    connection.execute(CREATE_TABLE_SQL)
    connection.execute(INSERT_TABLE_SQL, 1, 'Tom', '1980-02-26', 0)
    connection.execute(INSERT_TABLE_SQL, 2, 'Dick', '1982-03-14', 3)
    connection.execute(INSERT_TABLE_SQL, 3, 'Harry', '1972-11-24', 2)


def drop_db(sqlalchemy_uri):
    engine = create_engine(config.SQLA_URI)
    meta = MetaData(bind=engine)
    meta.reflect()
    meta.drop_all()
