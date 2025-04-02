"""
Manages logging to a sqlite database for the chat server.
"""
from enum import Enum
import sqlite3
from typing import Final

from z_module.network.connection import Connection
from z_module.io.sqlite import SQLite, SQLField, SQLFieldType
from z_module.validation import enforce_parameter_types
from z_module.io.sqlite import _SqlInsert

# SQL Table names
USER_TABLE: Final[str]         = 'user'
USER_HISTORY_TABLE: Final[str] = 'user_history'
LOG_TYPE_TABLE: Final[str]     = 'log_type'
LOG_TABLE: Final[str]          = 'log'

class LogType(Enum):
    """Enum of the logging types for the server."""
    ERROR = 1
    WARNING = 2
    INFO = 3
    SUCCESS = 4

class SQLManager(SQLite):
    """Manages sql database for the server."""
    SCHEMA_USER: Final[list[SQLField]] = [
        SQLField(f_name='id',
                 f_type=SQLFieldType.INTEGER,
                 f_not_null=True,
                 f_primary=True,
                 f_auto_increment=True,
                 f_unique=True),
        SQLField(f_name='ts',
                 f_type=SQLFieldType.TIMESTAMP,
                 f_not_null=True,
                 f_default="(strftime('%s', 'now'))"),
        SQLField(f_name='name',
                 f_type=SQLFieldType.TEXT,
                 f_not_null=True,
                 f_unique=True),
        SQLField(f_name='password',
                 f_type=SQLFieldType.TEXT,
                 f_not_null=True)]

    SCHEMA_USER_HIST: Final[list[SQLField]] = [
        SQLField(f_name='id',
                 f_type=SQLFieldType.INTEGER,
                 f_not_null=True,
                 f_primary=True,
                 f_auto_increment=True,
                 f_unique=True),
        SQLField(f_name='ts',
                 f_type=SQLFieldType.TIMESTAMP,
                 f_not_null=True,
                 f_default="(strftime('%s', 'now'))"),
        SQLField(f_name='from',
                 f_type=SQLFieldType.INTEGER,
                 f_not_null=True),
        SQLField(f_name='to',
                 f_type=SQLFieldType.INTEGER)]

    SCHEMA_LOG_TYPE: Final[list[SQLField]] = [
        SQLField(f_name='id',
                 f_type=SQLFieldType.INTEGER,
                 f_not_null=True,
                 f_primary=True,
                 f_auto_increment=True,
                 f_unique=True),
        SQLField(f_name='text',
                 f_type=SQLFieldType.TEXT,
                 f_not_null=True,
                 f_unique=True)]

    SCHEMA_LOG: Final[list[SQLField]] = [
        SQLField(f_name='id',
                 f_type=SQLFieldType.INTEGER,
                 f_not_null=True,
                 f_primary=True,
                 f_auto_increment=True,
                 f_unique=True),
        SQLField(f_name='ts',
                 f_type=SQLFieldType.TIMESTAMP,
                 f_not_null=True,
                 f_default="(strftime('%s', 'now'))"),
        SQLField(f_name='type',
                 f_type=SQLFieldType.INTEGER,
                 f_not_null=True),
        SQLField(f_name='message',
                 f_type=SQLFieldType.TEXT)]

    def __init__(self, file: str = SQLite.DEFAULT_DATABASE):
        tables_schemas: dict[str, list[SQLField]] = {
            USER_TABLE        :SQLManager.SCHEMA_USER,
            USER_HISTORY_TABLE:SQLManager.SCHEMA_USER_HIST,
            LOG_TYPE_TABLE    :SQLManager.SCHEMA_LOG_TYPE,
            LOG_TABLE         :SQLManager.SCHEMA_LOG
        }
        super().__init__(file, tables_schemas)
        #TODO: if create database populate default values (such as log_type)

    # def _validate_database_schema(self, tables_schemas: dict[str, list[SQLField]]):
    #     """Validate the database schema."""
    #     for name, schema in self._tables_schemas.items():
    #         if not self._validate_table_exists(name):
    #             raise sqlite3.Error(f'Table {name} does not exist.')
    #         if not self._validate_table_schema(name, schema):
    #             raise sqlite3.Error(f'Table {name} does not match the schema.')

    def add_new_user(self) -> None:
        """
        """
        if self._db_conn is None:
            self._connect_sql_database()

        #TODO

        self._close_sql_connection()

    def get_user_by_id(self):
        if self._db_conn is None:
            self._connect_sql_database()

        #TODO

        self._close_sql_connection()

    def get_user_id_by_name(self, user_name: str) -> int:
        """Gets a user id by its name from the database.
        
        Args:
            user_name: The user account name
        
        Returns:
            Returns the user id from the user table or 0 when not found.
        """
        if self._db_conn is None:
            self._connect_sql_database()

        user_id: int = 0
        command = 'SELECT id FROM "user" WHERE name = ?;'

        # Get user id
        try:
            cursor = self._db_conn.cursor()
            cursor.execute(command, user_name)
        except sqlite3.Error:
            # If the name is not in the database there is no associated account.
            pass
        else:
            if result := cursor.fetchone():
                user_id = result[0]

        self._close_sql_connection()

        return user_id

    @enforce_parameter_types
    def add_new_log(self, log_type: LogType, message: str) -> bool:
        """Add a new log to the database.
        
        Args:
            log_type: Type of log entry
            message: message to attach to the log entry
        
        Returns:
            True if successful
        """
        if self._db_conn is None:
            self._connect_sql_database()

        values: _SqlInsert = {
            'type':log_type.value,
            'message':message
            }

        result: bool = self._insert_into_table(LOG_TABLE, values)

        self._close_sql_connection()

        return result

    @enforce_parameter_types
    def add_new_user_history(self,
                             message: str,
                             from_conn: Connection,
                             to_conn: Connection | None = None) -> bool:
        """Add a user history entry.

        Args:
            message: Generally what the user say/whisper
            from_conn: The sending connection
            to_conn: The receiving connection or None if not a whisper
        
        Returns:
            True on success
        """
        if self._db_conn is None:
            self._connect_sql_database()

        # NOTE: currently non-logged in users are consider id 0
        # could just require every user to make an account
        # to_id being 0 also indicates it is a say and not a whisper
        from_id: int = self.get_user_id_by_name(from_conn.user_name)
        to_id: int   = 0

        if to_conn is not None:
            to_id = self.get_user_id_by_name(to_conn.user_name)

        values: _SqlInsert = {
            'from':from_id,
            'to':to_id,
            'message':message
            }

        result: bool = self._insert_into_table(USER_HISTORY_TABLE, values)

        self._close_sql_connection()

        return result

# -- Create the orders table
# CREATE TABLE IF NOT EXISTS orders (
#     order_id INTEGER PRIMARY KEY,
#     user_id INTEGER NOT NULL,
#     product TEXT NOT NULL,
#     FOREIGN KEY (user_id) REFERENCES users(id)
# );