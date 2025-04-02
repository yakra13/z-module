"""
Sqlite wrapper for sqlite3
"""
import os
import sqlite3
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Tuple, Union

from z_module.validation import enforce_parameter_types

# typedef
_SqlInsert = dict[str, Union[str, int, float]]

class SQLFieldType(Enum):
    """Enum to map field value types."""
    INTEGER   = 0
    TEXT      = auto()
    BLOB      = auto()
    REAL      = auto()
    NUMERIC   = auto()
    TIMESTAMP = auto()

@dataclass
class SQLField():
    """Dataclass representing a table field."""
    f_name: str
    f_type: SQLFieldType
    f_not_null: bool       = field(default=False)
    # NOTE: can have multiple primary keys unless auto increment
    f_primary: bool        = field(default=False)
    # NOTE: only the primary key can auto increment and their can be only 1 primary key
    f_auto_increment: bool = field(default=False)
    f_unique: bool         = field(default=False)
    f_default: str         = field(default=None)
    f_check: str           = field(default=None)

    def to_sql_pragma(self) -> Tuple[str, str, int, str | None, int]:
        """Converts to expected format for sqlite."""
        return (self.f_name,
                self.f_type.name,
                int(self.f_not_null),
                self.f_default,
                int(self.f_primary))


class SQLite():
    """A sqlite3 wrapper."""
    DEFAULT_DATABASE: str = 'sqlite.db'

    # @enforce_parameter_types
    def __init__(self,
                 file: str,
                 tables_schemas: dict[str, list[SQLField]]):
        #TODO validate file path
        #TODO create based on bool
        self._db_conn: sqlite3.Connection = None
        self._file: str = file
        self._tables_schemas: dict[str, list[SQLField]] = tables_schemas

    @enforce_parameter_types
    def create_database(self) -> None:
        """Create the database."""
        if self._db_conn is None:
            self._connect_sql_database()

        self._build_database()

        self._close_sql_connection()

    @enforce_parameter_types
    def _connect_sql_database(self, validate_schema: bool = False) -> None:
        """Attempts to connect to a database.

        If successful can validate the database schema. If the database is empty then
        validation will fail or if it does not match the passed in table schema.

        Raises:
            sqlite3.Error: General sql error
            RuntimeError: The database schema does not match.
        """
        if self._db_conn:
            return

        self._db_conn = sqlite3.connect(self._file)

        if validate_schema and not self._validate_database_schema():
            self._close_sql_connection()
            raise RuntimeError(f'{self._file} database schema is invalid.')

    def _close_sql_connection(self) -> None:
        """Attempts to close the database connection.
        
        It is good practice to close the connection when you are done with it.
        """
        if not self._db_conn:
            return

        self._db_conn.close()
        self._db_conn = None

    @enforce_parameter_types
    def _validate_table_exists(self, table_name: str) -> bool:
        cursor = self._db_conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?",
                       (table_name,))
        return cursor.fetchone() is not None

    @enforce_parameter_types
    def _validate_table_schema(self, table_name: str, fields: list[SQLField]) -> bool:
        cursor = self._db_conn.cursor()
        cursor.execute(f'PRAGMA table_info({table_name})')
        columns = cursor.fetchall()

        # columns: name, type, notnull, dflt_value, pk
        column_info = [(col[1], col[2], col[3], col[4], col[5]) for col in columns]

        return set(column_info) == set([f.to_sql_pragma() for f in fields])

    @enforce_parameter_types
    def _validate_database_schema(self) -> bool:
        """Validate the database schema."""
        for name, schema in self._tables_schemas.items():
            if not self._validate_table_exists(name):
                return False
            if not self._validate_table_schema(name, schema):
                return False
        return True

    @enforce_parameter_types
    def _build_database(self) -> bool:
        """Build a database from scratch."""
        for name, schema in self._tables_schemas.items():
            if not self._create_table(name, schema):
                return False
        return True

    @enforce_parameter_types
    def _create_table(self,
                     table_name: str,
                     fields: list[SQLField],
                     if_not_exists: bool = True):
        # TODO validate
        auto_increment: str = ''
        primary_keys: list[str] = []
        properties: str

        for f in fields:
            properties += f'\t"{f.f_name}"\t'
            properties += f'{f.f_type.name}'
            properties += f"{' NOT NULL' if f.f_not_null else ''}"
            properties += f"{' DEFAULT ' + f.f_default if f.f_default else ''}"
            properties += f"{' CHECK(' + f.f_check + ')' if f.f_check else ''}"
            # properties += f"{' UNIQUE,\n' if f.f_unique else ',\n'}"
            properties += ' {val},\n'.format(val='UNIQUE' if f.f_unique else '')
            if f.f_auto_increment:
                auto_increment = 'AUTOINCREMENT'
            if f.f_primary:
                primary_keys.append(f'"{f.f_name}"')

        if len(primary_keys) > 1:
            auto_increment = ''

        command = 'CREATE TABLE '
        command += f"{'IF NOT EXISTS ' if if_not_exists else ''}"
        command += f"\"{table_name}\" (\n"
        command += properties
        command += f"\tPRIMARY KEY({', '.join(primary_keys)} {auto_increment})\n"
        command += ');'

        try:
            cursor = self._db_conn.cursor()

            cursor.execute(command)
            self._db_conn.commit()
        except sqlite3.Error:
            return False

        return True

    @enforce_parameter_types
    def _insert_into_table(self, table: str, values: _SqlInsert):
        command = f"INSERT INTO \"{table}\" ({', '.join(values.keys())})\n"
        command += f"VALUES ({', '.join(['?' for _ in range(len(values))])})"

        try:
            cursor = self._db_conn.cursor()
            cursor.execute(command, *values.values())
            self._db_conn.commit()
        except sqlite3.Error:
            return False

        return True
