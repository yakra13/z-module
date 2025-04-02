"""
Client that connects to a server.
"""
import bisect
import socket
from _thread import LockType
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
from typing import Final, Tuple

from z_module.network.connection import Connection
from z_module.network.message import Builder, Message, MessageType
from z_module.security.password import create_username_and_password
from z_module.security.password import _UserNamePassword
from z_module.security.password import MIN_PASSWORD_LEN
from z_module.types.int import UInt16, UInt64
from z_module.validation import Validate, enforce_parameter_types

# Const values
DEFAULT_USERNAME: Final[str] = '(not logged in)'
MAX_WORKERS: Final[int]      = 5

class Client():
    """Client object for communication with a server."""

    def __init__(self) -> None:
        self._conn: Connection = None
        #TODO in gui handle flushing this buffer
        self.message_buffer: list[str] = []
        #TODO in gui handle displaying this info
        self._peers: list[str] = []

        self._tp_exec: ThreadPoolExecutor = ThreadPoolExecutor(max_workers=MAX_WORKERS)
        self._tp_lock: LockType = Lock()

    @property
    def peers(self) -> list[str]:
        """Returns the list of peers connected to the server."""
        return self._peers

    @property
    def is_connected(self) -> bool:
        """Returns the is connected state of the connection."""
        if self._conn:
            return self._conn.is_connected
        return False

    @enforce_parameter_types
    def _add_to_peer_list(self, name: str) -> None:
        """"""
        if name not in self._peers:
            bisect.insort_left(self._peers, name)

    @enforce_parameter_types
    def _remove_from_peer_list(self, name: str) -> None:
        """"""
        if name in self._peers:
            self._peers.remove(name)

    @enforce_parameter_types
    def _rename_peer_in_peer_list(self, old_name: str, new_name: str) -> None:
        """"""
        self._remove_from_peer_list(old_name)
        self._add_to_peer_list(new_name)

    def _handle_connection(self) -> None:
        """Thread handler for receiving messages."""
        print('handler started')
        while self._conn.is_closing is False:
            # self._tp_lock.acquire()
            data: bytes = self._conn.recv_bytes()

            if not data:
                self._process_message_queue()
                continue

        self._conn = None

    def _process_message_queue(self):
        """"""
        #fill some buffer that others can pop from
        m: Message = None
        while (m := self._conn.message_queue.pop()) is not None:
            if m.is_malformed:
                continue

            match m.id:
                case MessageType.INFO_CLIENT_CONN:
                    try:
                        connected_name: str = m.get_next_field()
                    except IndexError as err:
                        self._conn.send_bytes(Builder.error_malformed_data(err))
                        continue

                    self._add_to_peer_list(connected_name)

                case MessageType.INFO_CLIENT_DISC:
                    try:
                        disconnected_name: str = m.get_next_field()
                    except IndexError as err:
                        self._conn.send_bytes(Builder.error_malformed_data(err))
                        continue

                    self._remove_from_peer_list(disconnected_name)

                case MessageType.INFO_CLIENT_UPDATE:
                    try:
                        old_name: str = m.get_next_field()
                        new_name: str = m.get_next_field()
                    except IndexError as err:
                        self._conn.send_bytes(Builder.error_malformed_data(err))
                        continue

                    self._rename_peer_in_peer_list(old_name, new_name)

                case MessageType.INFO_CLIENT_LIST:
                    self._peers.clear()
                    while True:
                        try:
                            p: str = m.get_next_field()
                        except IndexError as err:
                            break
                        self._add_to_peer_list(p)

                case MessageType.SUC_CONNECT | MessageType.SUC_LOGOUT:
                    try:
                        temp_user_name: str = m.get_next_field()
                    except IndexError as err:
                        self._conn.send_bytes(Builder.error_malformed_data(err))
                        continue

                    self._conn.user_name = temp_user_name

                    if m.id == MessageType.SUC_LOGOUT:
                        self._conn.is_logged_in = False
                        self.message_buffer.append('Successfully logged out.')
                    else:
                        self.message_buffer.append('Successfully connected.')

                case MessageType.SUC_GENERIC | MessageType.SUC_USER_CREATE | MessageType.SUC_LOGIN:
                    try:
                        message: str = m.get_next_field()
                    except IndexError as err:
                        self._conn.send_bytes(Builder.error_malformed_data(err))
                        continue

                    self.message_buffer.append(message)

                    if m.id == MessageType.SUC_LOGIN:
                        self._conn.is_logged_in = True

                case MessageType.ERR_GENERIC | MessageType.ERR_LOGIN | \
                     MessageType.ERR_MALFORMED_DATA | MessageType.ERR_USER_EXISTS | \
                     MessageType.ERR_USER_OFFLINE:
                    try:
                        message: str = m.get_next_field()
                    except IndexError as err:
                        self._conn.send_bytes(Builder.error_malformed_data(err))
                        continue

                    self.message_buffer.append(message)

                case MessageType.SVR_MESSAGE:
                    try:
                        message: str = m.get_next_field()
                    except IndexError as err:
                        self._conn.send_bytes(Builder.error_malformed_data(err))
                        continue

                    self.message_buffer.append(message)

                case MessageType.SVR_CLIENT_SAY:
                    try:
                        from_user: str = m.get_next_field()
                        message: str = m.get_next_field()
                    except IndexError as err:
                        self._conn.send_bytes(Builder.error_malformed_data(err))
                        continue

                    self.message_buffer.append(f'{from_user} says: {message}')

                case MessageType.SVR_CLIENT_WHISPER:
                    try:
                        from_user: str = m.get_next_field()
                        message: str = m.get_next_field()
                    except IndexError as err:
                        self._conn.send_bytes(Builder.error_malformed_data(err))
                        continue

                    self.message_buffer.append(f'{from_user} whispers: {message}')

                case _:
                    fields: list[int] = []
                    while True:
                        try:
                            f = m.get_next_field()
                        except IndexError:
                            break
                        fields.append(f)
                    self.message_buffer.append(f'{m.id} not implemented: {fields}')

    @enforce_parameter_types
    def connect_to_server(self, addr: str, port: UInt16) -> bool:
        """Attempt to connect to the specified server.
        
        Args:
            addr: The server address.
            port: The server port.
            
        Returns:
            True if successfully connects.
        """
        if self._conn is not None:
            return False

        sock: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(Connection.DEFAULT_TIMEOUT)

        try:
            sock.connect((addr, port.value))
        except (ConnectionRefusedError, TimeoutError, InterruptedError):
            return False

        self._conn = Connection(sock,
                                addr,
                                port,
                                'temp_user_name',
                                UInt64(Connection.DEFAULT_BUFF_SIZE),
                                self._tp_lock)
        self._conn.is_connected = True

        try:
            self._tp_exec.submit(self._handle_connection)
        except RuntimeError:
            # Thread Pool was shutdown and needs to be recreated
            self._tp_exec = ThreadPoolExecutor(max_workers=MAX_WORKERS)
            self._tp_exec.submit(self._handle_connection)

        return True

    @enforce_parameter_types
    def req_create_user(self, user_name: str, password: str) -> Tuple[bool, str]:
        """Attempt to register a new user with the server.
        
        Args:
            user_name: New user account name.
            password: Plain text password.
        
        Returns:
            True if the request was sent. Does not imply account create success.
        """
        if self._conn is None:
            return False, 'Error creating new user: Not connected to the server.'

        try:
            Validate.start(password).length_in_range(MIN_PASSWORD_LEN, UInt16.MAX).regex_str()
        except (TypeError, ValueError):
            return False, 'Invalid password: Must be at least {MIN_PASSWORD_LEN} characters and ' \
                'contain at least 1 lower case, upper case, special character and number.'

        result: _UserNamePassword = create_username_and_password(user_name, password)
        if result is None:
            return False, 'Invalid password: Must be at least {MIN_PASSWORD_LEN} characters and ' \
                'contain at least 1 lower case, upper case, special character and number.'

        self._conn.send_bytes(Builder.request_user_create(result[0], result[1]))

        return True, f'Successfully requested to make new user: {user_name}'

    def req_disconnect(self) -> None:
        """Disconnects from the current server."""
        if self._conn is None:
            print('CONN IS NONE')
            return
        print('SENDING REQ DISCONNECT')
        self._conn.send_bytes(Builder.request_disconnect())

        # Will cause the handler thread to complete and set self._conn to None
        self._conn.close_connection()

        # Reset attributes
        self._peers.clear()
        self.message_buffer.clear()

    @enforce_parameter_types
    def req_login(self, user_name: str, password: str) -> Tuple[bool, str]:
        """Attempts to login to the server.
        
        Args:
            user_name: User account to log in to.
            password: Plain text password.
            
        Returns:
            True if the request was sent. Does not imply login success.
        """
        if self._conn is None:
            return False, 'Not connected to a server.'

        if self._conn.is_logged_in is True:
            return False, 'Error logging in: You are already logged in.'

        #TODO The passwords are not actually secure currently. This is just simplified.
        result: _UserNamePassword = create_username_and_password(user_name, password)

        #TODO Perform Validate in the gui for name and pass
        if result is None:
            return False, 'Error logging in: User name is not valid.'

        self._conn.send_bytes(Builder.request_user_login(result[0], result[1]))

        return True, f'Successfully sent login request as: {user_name}'

    def req_logout(self) -> bool:
        """Attempts to log out of the server."""
        self._conn.send_bytes(Builder.request_user_logout())

    @enforce_parameter_types
    def req_say(self, message: str) -> bool:
        """Send a say message to the server.
        
        Args:
            message: The message to be sent.
            
        Returns:
            True if request sent successfully. Does not imply say success.
        """
        if self._conn is None:
            return False

        self._conn.send_bytes(Builder.request_say(message))

        return True

    @enforce_parameter_types
    def req_whisper(self, user_name: str, message: str) -> bool:
        """Send a whisper to the specified user.
        
        Args:
            user_name: The user to whisper.
            message: The whisper to be sent.

        Returns:
            True if request sent successfully. Does not imply whisper success.
        """
        if self._conn is None:
            return False

        self._conn.send_bytes(Builder.send_whisper(user_name, message))

        return True
