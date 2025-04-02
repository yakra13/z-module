"""
Handles and defines a connection between 2 hosts/servers.
"""
import socket
import time
from copy import deepcopy
from typing import Final
from _thread import LockType

from z_module.network.message import Builder, Message, MessageQueue
from z_module.types.int import UInt8, UInt16, UInt32, UInt64
from z_module.validation import Validate
from z_module.validation import enforce_parameter_types


class Connection():
    """Represents a connection to a client."""
    DEFAULT_BUFF_SIZE: Final[UInt64] = UInt64(4)
    DEFAULT_TIMEOUT: Final[int]   = 1
    HISTORY_LENGTH: Final[int]    = 64 # Number of history entries before writing to log

    @enforce_parameter_types
    def __init__(self,
                 sock: socket.socket,
                 address: str,
                 port: UInt16,
                 user_name: str,
                 buffer_size: UInt64,
                 tp_lock: LockType):

        Validate.start(address).not_empty().is_ip_address()
        # Validate.start(port).in_range(1, UInt16.MAX)
        Validate.start(user_name).length_in_range(4, UInt8.MAX)
        Validate.start(buffer_size).in_range(Connection.DEFAULT_BUFF_SIZE, UInt64.MAX)

        self._socket: socket.socket = sock

        self._address: str = address
        self._port: UInt16 = port

        self._user_id: UInt32     = 0
        self.user_name: str       = user_name
        self._buffer_size: UInt64 = buffer_size

        # TODO: think i can remove this and handle the locking in server.py
        self._tp_lock: LockType = tp_lock

        self.is_connected: bool = False
        self.is_logged_in: bool = False
        self._is_closing: bool  = False

        self.time_connected: float  = time.time()
        self.time_login: float      = 0.0
        self._time_last_recv: float = 0.0

        self.message_queue: MessageQueue = MessageQueue()

        self._message_history: list[Message] = []

    @property
    def is_closing(self) -> bool:
        """If the connection is closing."""
        return self._is_closing

    @property
    def message_history(self) -> list[Message]:
        """Returns a deep copy of the message history."""
        return deepcopy(self._message_history)

    @property
    def history_length(self) -> int:
        """Returns to number of entries in message history."""
        return len(self._message_history)

    def clear_history(self) -> None:
        """Empty the message history."""
        self._message_history.clear()

    def close_connection(self) -> None:
        """Closes this connection.
        
        Sets the connections state to closing.
        Messages the client/server that its connection is being closed.
        Closes the connection socket.
        """
        self._is_closing = True
        self.is_connected = False
        # A client receiving this is being shut down by the server.
        # A server receiving this is being informed by the client it is disconnecting.
        self._socket.sendall(Builder.request_disconnect())

        self._socket.close()

    def recv_bytes(self) -> bytes | None:
        """Buffer bytes from this connection.

        May return a partial message if a socket error occurs during recv().

        Args:
            buffer_size: Size of buffer to fill.
        
        Returns:
            Bytes recv'd from this connection or None on timeout.
        """
        data: bytes = b''
        buffer: bytes = b''
        bytes_remaining: int = None

        while True:
            try:
                buffer = self._socket.recv(self._buffer_size.value)

                if not buffer:
                    break

                data += buffer

                if bytes_remaining is None:
                    dlb = data[Message.TYPE_FLD_LEN:Message.TYPE_FLD_LEN + Message.SIZE_FLD_LEN]
                    bytes_remaining = int.from_bytes(dlb, 'big')
                # Subtract the received bytes
                bytes_remaining -= self._buffer_size.value
                # Continue receiving bytes
                if bytes_remaining > 0:
                    continue
            except socket.timeout:
                print(f'{self.user_name} socket timeout')
                #TODO: Socket timed out but thats ok.
                # Verify client is still connected before shutting down.
                # handle this in the server for now
                break
            except (ConnectionAbortedError, ConnectionResetError, OSError):
                self._is_closing = True
                #TODO may return partial data
                break

            self._time_last_recv = time.time()

            try:
                message: Message = Builder.parse_message(data)
            except ValueError as err:
                return f'{err}'
            except BufferError as err:
                return f'{err}'

            self.message_queue.push(message)
            print(message)

        return data

    @enforce_parameter_types
    def send_bytes(self, data: bytes) -> bool:
        """Sends byte data over the connection.
        
        Args:
            data: bytes to be sent
        
        Returns:
            True if sendall succeeds
        """
        print("send all bytes!!!!")
        with open('test.txt', 'w', encoding='utf-8') as f:
            f.write(data.hex())

        try:
            self._socket.sendall(data)
            print("sent all bytes")
        except (BrokenPipeError, ConnectionResetError):
            self._is_closing = True
        except socket.timeout:
            #TODO: Future possible slightly different actions on a send timeout.
            self._is_closing = True
        else:
            print('return true')
            return True
        print('return false')
        return False
