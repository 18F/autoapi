import config
import utils


import pytest
from sqlalchemy import create_engine, inspect, MetaData
from sqlalchemy.sql import select


def assert_column_type(column, expected_type):
    assert column.type.python_type == expected_type


def assert_columns_have_non_unique_indexes(engine, table_name, *columns):
    inspection = inspect(engine)

    non_unique_1_column_indexes = [
        index['column_names'][0]
        for index in inspection.get_indexes(table_name)
        if not index['unique'] and len(index['column_names']) == 1
    ]

    assert set(columns) <= set(non_unique_1_column_indexes)


class TestLoadTable():
    def setup_method(self, method):
        self.engine = create_engine(config.SQLA_URI)
        self.meta = MetaData(bind=self.engine)

    def teardown_method(self, method):
        self.meta.drop_all()

    def load_table(self, tmpdir, csv_str, table_name, **kwargs):
        file_name = '{}.csv'.format(table_name)
        csv_file = tmpdir.join(file_name)
        csv_file.write(csv_str)

        utils.load_table(str(csv_file), table_name, **kwargs)
        self.meta.reflect()

    def test_good_csv(self, tmpdir):
        CSV = """name, dob, number_of_pets
        Tom, 1980-02-26, 0
        Dick, 1982-03-14, 3
        Harry, 1972-11-24, 2
        """

        self.load_table(tmpdir, CSV, 'people')

        assert 'people' in self.meta.tables
        people = self.meta.tables['people']

        assert_column_type(people.columns['index'], int)
        assert_column_type(people.columns['name'], str)
        assert_column_type(people.columns['dob'], str)
        assert_column_type(people.columns['number_of_pets'], str)

        assert people.columns['index'].primary_key is True
        assert people.columns['name'].primary_key is False

        assert_columns_have_non_unique_indexes(self.engine, 'people', 'name',
                                               'dob', 'number_of_pets')

        connection = self.engine.connect()
        results = connection.execute(
            select([people]).order_by(people.c.index)).fetchall()
        assert (0, 'Tom', '1980-02-26', '0') == results[0]
        assert (1, 'Dick', '1982-03-14', '3') == results[1]
        assert (2, 'Harry', '1972-11-24', '2') == results[2]

    def test_load_with_chunking(self, tmpdir):
        CSV = """name, dob, number_of_pets
        Tom, 1980-02-26, 0
        Dick, 1982-03-14, 3
        Harry, 1972-11-24, 2
        """

        self.load_table(tmpdir, CSV, 'people', chunksize=1)

        people = self.meta.tables['people']

        connection = self.engine.connect()
        results = connection.execute(
            select([people]).order_by(people.c.index)).fetchall()
        assert (0, 'Tom', '1980-02-26', '0') == results[0]
        assert (1, 'Dick', '1982-03-14', '3') == results[1]
        assert (2, 'Harry', '1972-11-24', '2') == results[2]

    def test_empty_csv(self, tmpdir):
        file_name = 'empty.csv'
        csv_file = tmpdir.join(file_name)
        csv_file.ensure()

        with pytest.raises(Exception):
            utils.load_table(str(csv_file), 'empty')

    def test_embedded_space_in_columnname(self, tmpdir):
        CSV = """name, number of pets
        Tom, 0
        Dick, 3
        Harry, 2
        """

        self.load_table(tmpdir, CSV, 'people')
        people = self.meta.tables['people']

        assert 'number of pets' in people.columns

    def test_null_empty_string_handling(self, tmpdir):
        CSV = """name, number_of_pets
        Tom, 0
        "", 3
        , 2
        """

        self.load_table(tmpdir, CSV, 'people')

        people = self.meta.tables['people']

        connection = self.engine.connect()
        results = connection.execute(
            select([people]).order_by(people.c.index)).fetchall()
        assert (0, 'Tom', '0') == results[0]
        assert (1, None, '3') == results[1]
        assert (2, None, '2') == results[2]

    def test_embedded_space_in_tablename_and_filename(self, tmpdir):
        CSV = """name, number_of_pets
        Tom, 0
        Dick, 3
        Harry, 2
        """
        self.load_table(tmpdir, CSV, 'We the people')

        assert 'We the people' in self.meta.tables
