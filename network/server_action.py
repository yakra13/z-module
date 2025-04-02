"""
"""
from typing import Final

from z_module.network.connection import Connection
from z_module.network.message import Builder
from z_module.network.server_sql_manager import SQLManager
from z_module.validation import enforce_parameter_types
from z_module.utility.z_utility import change_dict_key
from z_module.network.types import _Connections

# Password format validation.
HASH_LENGTH: Final[int] = 64

class ServerActionManager():
    """Collection of server request actions."""

    def __init__(self, sql_manager: SQLManager) -> None:
        self._sql_manager: SQLManager = sql_manager

    @enforce_parameter_types
    def create_user(self, user_name: str, password_hash: str) -> bytearray:
        """Create a new user.
        
        Args:
            user_name: User name for the new user.
            password_hash: The hashed password for the new user.
            
        Returns:
            Bytearray response for the requester.
        """

        #TODO: you could create a user name that is the same as a temp user name and thats bad
        if user := self._sql_manager.get_user_by_name(user_name):
            #TODO use user for stuff?
            return Builder.error_user_exists()

        if len(password_hash) != HASH_LENGTH:
            return Builder.error_malformed_data()

        if self._sql_manager.add_new_user(user_name, password_hash):
            return Builder.success_user_created(f'Successfully created user {user_name}')
        else:
            return Builder.error_generic('User not created.')

    @enforce_parameter_types
    def login_user(self,
                   conn: Connection,
                   user_name: str,
                   password_hash: str,
                   conns: _Connections) -> bytearray:
        """Log in a specified user.
        
        Args:
            conn: The Connection requesting to login.
            user_name: User name to log in.
            password_hash: Hashed password to use.
            
        Returns:
            A bytearray response message for the requester.
        """
        if user := self._sql_manager.get_user_by_name(user_name):
            #TODO: user exists grab the passhash field
            #if user.password == password_hash:
            raise NotImplementedError(user)
            if change_dict_key(conn.name, user_name, conns):
                conn.login(user_name)
            else:
                return Builder.error_login(f'{user_name} is already logged in.')

            #TODO
            # self._sql_manager.add_new_log(log type, message)
            return Builder.success_login()

        return Builder.error_login(f'No account for {user_name} exists.')

    @enforce_parameter_types
    def broadcast(self, message: str, conns: _Connections, ignore: list[str] = None) -> None:
        """Broadcast a message to all connections

        Args:
            message: The message to broadcast.
            ignore: List of (address,port) to skip.
        
        Returns:
            None.
        """
        if ignore is None:
            ignore = []

        for name, conn in conns.items():
            if name not in ignore:
                conn.send_bytes(Builder.send_server_message(message))

    @enforce_parameter_types
    def broadcast_client_connect(self, client: Connection, conns: _Connections) -> None:
        """Inform all clients of a new connection.
        
        Args:
            client: The new connection.
            conns: Dict of Connections to message. 
        
        Returns:
            None.
        """
        for _, conn in conns.items():
            if conn == client:
                continue
            conn.send_bytes(Builder.send_client_connect(client.user_name))

    @enforce_parameter_types
    def broadcast_client_disconnect(self, client: Connection, conns: _Connections) -> None:
        """Inform all clients of a client disconnection.
        
        Args:
            client: Name of the disconnection.
            conns: Dict of Connections to message. 
        
        Returns:
            None.
        """
        for name, conn in conns.items():
            if conn == client:
                continue
            conn.send_bytes(Builder.send_client_disconnect(client.user_name))

    @enforce_parameter_types
    def broadcast_client_update(self,
                                old_name: str,
                                client: Connection,
                                conns: _Connections) -> None:
        """Inform all clients of any client data to be updated.
        
        Args:
            old_name: Clients previous name.
            client: Clients updated name.
            conns: Dict of Connections to message. 
        
        Returns:
            None.
        """
        for _, conn in conns.items():
            if conn == client:
                continue
            conn.send_bytes(Builder.send_client_update(old_name, client.user_name))

    @enforce_parameter_types
    def send_connections(self, conn: Connection, conns: _Connections) -> bool:
        """Send connection information to to target connection.

        Args:
            to_conn: Client connection to send data.
            conns: Dict of Connections to get data from. 
        
        Returns:
            None.
        """
        print('in send connections')
        client_names: list[str] = []
        for name, _ in conns.items():
            print(f'looping names {name}')
            print(f'looping names {name}')
            print(f'looping names {conns}')
            if name == conn.user_name:
                print('found own name')
                continue
            client_names.append(name)

        print('exit loop')

        if len(client_names) < 1:
            print('there are no clients to send this conn too')
            return True

        sorted_list = sorted(client_names)
        print('ok send the bytes')
        return conn.send_bytes(Builder.send_all_clients(sorted_list))

    @enforce_parameter_types
    def whisper(self, to_conn: Connection, from_conn: Connection, message: str) -> None:
        """Whispers a specified user.

        Args:
            to_conn: Client connection to send whisper.
            from_user: Name of the whisperer.
            message: The whisper being sent. 
        
        Returns:
            None.
        """
        to_conn.send_bytes(Builder.send_whisper(from_conn.user_name, message))
