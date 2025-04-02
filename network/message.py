"""
Handles message format, creation, and parsing.
"""
import struct
import time
from enum import auto
from typing import Final, Iterator, Tuple
from z_module.utility.z_base import Singleton, ByteEnum
from z_module.validation import enforce_parameter_types

# constants
BUFFER_MIN: Final[int] = 4

MAX_FIELD_CNT: Final[int]  = 4 # TODO Does not work with send all clients
MAX_FIELD_LEN: Final[int]  = 1024 # Used to control size of message string

MSG_COUNTER_MASK: Final[int] = 0xFFFF

class MessageType(ByteEnum):
    """Enum of valid message types to handle. Start 0x80"""
    # Client -> Server
    REQ_CREATE_USER: Final[bytes]    = b'\x80'
    REQ_DISCONNECT: Final[bytes]     = auto()
    REQ_LOGIN: Final[bytes]          = auto()
    REQ_LOGOUT: Final[bytes]         = auto()
    REQ_SAY: Final[bytes]            = auto()
    REQ_WHISPER: Final[bytes]        = auto()
    # Client <- Server
    INFO_CLIENT_CONN: Final[bytes]   = auto()
    INFO_CLIENT_DISC: Final[bytes]   = auto()
    INFO_CLIENT_UPDATE: Final[bytes] = auto()
    INFO_CLIENT_LIST: Final[bytes]   = auto()
    SUC_GENERIC: Final[bytes]        = auto()
    SUC_CONNECT: Final[bytes]        = auto()
    SUC_LOGIN: Final[bytes]          = auto()
    SUC_LOGOUT: Final[bytes]         = auto()
    SUC_USER_CREATE: Final[bytes]    = auto()
    ERR_GENERIC: Final[bytes]        = auto()
    ERR_LOGIN: Final[bytes]          = auto()
    ERR_MALFORMED_DATA: Final[bytes] = auto()
    ERR_USER_EXISTS: Final[bytes]    = auto()
    ERR_USER_OFFLINE: Final[bytes]   = auto()
    SVR_MESSAGE: Final[bytes]        = auto()
    SVR_CLIENT_WHISPER: Final[bytes] = auto()
    SVR_CLIENT_SAY: Final[bytes]     = auto()

class Message():
    """Stores the contents of a parsed message."""
    TYPE_FLD_LEN: Final[int] = 1 # Number of bytes in uint8
    SIZE_FLD_LEN: Final[int] = 2 # Number of bytes in uint16
    TIME_FLD_LEN: Final[int] = 8 # Number of bytes in double
    ID_FLD_LEN: Final[int]   = 2 # Number of bytes in uint16
    HEADER_LEN: Final[int]   = TYPE_FLD_LEN + SIZE_FLD_LEN + TIME_FLD_LEN + ID_FLD_LEN

    def __init__(self, message_type: MessageType,
                 length: int,
                 time_recv: float,
                 time_sent: float,
                 message_id: int,
                 fields: list[str],
                 malformed: bool = False) -> None:

        self._message_type: MessageType  = message_type
        self._message_length: int        = length
        self._message_id: int            = message_id

        self._time_recv: float   = time_recv
        self._time_sent: float   = time_sent
        self._is_malformed: bool = malformed

        self._fields: list[str] = fields


    @property
    def type(self) -> MessageType:
        """Returns the message type.
        
        The message type indicates how this message should be handled.
        It also dictates the number of fields that should be present.

        Use the field_count property to get the number of fields.
        """
        return self._message_type

    @property
    def length(self) -> int:
        """Returns the total bytes received in this message."""
        return self._message_length

    @property
    def field_count(self) -> int:
        """Returns the number of fields received.
        
        The field count should match what is expected based on the message type.
        For example, a user create request should have a count of 2.
        The first field containing the user name and the second containing
        the password hash.
        """
        return len(self._fields)

    @property
    def is_malformed(self) -> bool:
        """Returns whether the message is malformed or not.

        A malformed message is one where the number of bytes received
        did not match the number in the message length field.
        """
        return self._is_malformed

    @property
    def time_received(self) -> float:
        """Returns the time the message was received."""
        return self._time_recv

    @property
    def time_sent(self) -> float:
        """Returns the time the message was sent."""
        return self._time_sent

    @property
    def latency(self) -> float:
        """Returns the time taken for message to arrive."""
        return self._time_recv - self._time_sent

    def get_next_field(self) -> Iterator[str]:
        """Consumes the next field string.
        
        Calls to this function should be wrapped in try except block.
        
        Raises:
            IndexError: When iteration continues beyond the total fields
        
        Returns:
            Each field string.
        """
        for f in self._fields:
            try:
                yield f
            except StopIteration as exc:
                raise IndexError(self._message_type, 'Not enough fields in message.') from exc

class MessageQueue():
    """FIFO Queue for managing messages."""
    def __init__(self) -> None:
        self._queue: list[Message] = []

    def length(self) -> int:
        """Returns the length of the message queue."""
        return len(self._queue)

    def peek(self) -> Message | None:
        """Returns the top of the message queue without removing it."""
        try:
            return self._queue[0]
        except IndexError:
            return None

    def pop(self) -> Message | None:
        """Pops the top of the message queue."""
        try:
            return self._queue.pop(0)
        except IndexError:
            return None

    @enforce_parameter_types
    def push(self, message: Message) -> None:
        """Pops the top of the message queue."""
        self._queue.append(message)

class Builder(Singleton):
    """Network message builder."""
    # Dictionary to map MessageType to default message. Only the server has default messages.
    _default_messages: dict[MessageType, str] = {
        MessageType.SUC_GENERIC:'Unhelpful success message.',
        MessageType.SUC_LOGIN:'Logged in successfully.',
        MessageType.SUC_USER_CREATE:'User created successfully.',
        MessageType.ERR_LOGIN:'Incorrect user name or password.',
        MessageType.ERR_GENERIC:'Unhelpful error message.',
        MessageType.ERR_MALFORMED_DATA:'Malformed data received.',
        MessageType.ERR_USER_EXISTS:'User name already exists.',
        MessageType.ERR_USER_OFFLINE:'That user is not logged in.',
    }

    _message_counter: int = 0

    @classmethod
    @enforce_parameter_types
    def as_bytes(cls, message_type: MessageType) -> bytes:
        """Returns the byte value of a message type."""
        return int.from_bytes(message_type.value, 'little')

    # Client -> Server
    @classmethod
    @enforce_parameter_types
    def request_user_create(cls, user_name: str, password_hash: str) -> bytes:
        """Build a user create request."""
        # password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
        return cls._build_message(MessageType.REQ_CREATE_USER, user_name, password_hash)

    @classmethod
    @enforce_parameter_types
    def request_user_login(cls, user_name: str, password_hash: str) -> bytes:
        """Build a user login request."""
        # password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
        return cls._build_message(MessageType.REQ_LOGIN, user_name, password_hash)

    @classmethod
    def request_user_logout(cls) -> bytes:
        """Build a user login request."""
        # password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
        return cls._build_message(MessageType.REQ_LOGOUT)

    @classmethod
    def request_disconnect(cls) -> bytes:
        """Inform the server this client is disconnecting."""
        return cls._build_message(MessageType.REQ_DISCONNECT)

    @classmethod
    @enforce_parameter_types
    def request_say(cls, message: str) -> bytes:
        """Send a say message to all clients."""
        return cls._build_message(MessageType.REQ_SAY, message)

    @classmethod
    @enforce_parameter_types
    def request_whisper(cls, to_user: str, message: str) -> bytes:
        """Builds a whisper to message. Used by clients"""
        return cls._build_message(MessageType.REQ_WHISPER, to_user, message)

    # Client <- Server
    @classmethod
    @enforce_parameter_types
    def error_generic(cls, custom_message: str = None) -> bytes:
        """Build a generic error message."""
        if custom_message is None:
            custom_message = cls._default_messages[MessageType.ERR_GENERIC]
        return cls._build_message(MessageType.ERR_GENERIC, custom_message)

    @classmethod
    @enforce_parameter_types
    def error_login(cls, custom_message: str = None) -> bytes:
        """Build a login error message."""
        if custom_message is None:
            custom_message = cls._default_messages[MessageType.ERR_LOGIN]
        return cls._build_message(MessageType.ERR_LOGIN, custom_message)

    @classmethod
    @enforce_parameter_types
    def error_malformed_data(cls, custom_message: str = None) -> bytes:
        """Build a malformed data message."""
        if custom_message is None:
            custom_message = cls._default_messages[MessageType.ERR_MALFORMED_DATA]
        return cls._build_message(MessageType.ERR_MALFORMED_DATA, custom_message)

    @classmethod
    @enforce_parameter_types
    def error_user_exists(cls, custom_message: str = None) -> bytes:
        """Build a user exists message."""
        if custom_message is None:
            custom_message = cls._default_messages[MessageType.ERR_USER_EXISTS]
        return cls._build_message(MessageType.ERR_USER_EXISTS, custom_message)

    @classmethod
    @enforce_parameter_types
    def error_user_offline(cls, custom_message: str = None) -> bytes:
        """Build a user offline message."""
        if custom_message is None:
            custom_message = cls._default_messages[MessageType.ERR_USER_OFFLINE]
        return cls._build_message(MessageType.ERR_USER_OFFLINE, custom_message)

    @classmethod
    @enforce_parameter_types
    def success_generic(cls, custom_message: str = None) -> bytes:
        """Build a generic error message."""
        if custom_message is None:
            custom_message = cls._default_messages[MessageType.SUC_GENERIC]
        return cls._build_message(MessageType.SUC_GENERIC, custom_message)

    @classmethod
    @enforce_parameter_types
    def success_connect(cls, temp_user_name: str) -> bytes:
        """Responds a successful connection with temporary user name."""
        print('building success connect')
        return cls._build_message(MessageType.SUC_CONNECT, temp_user_name)

    @classmethod
    @enforce_parameter_types
    def success_user_created(cls, custom_message: str = None) -> bytes:
        """Build a user created message."""
        if custom_message is None:
            custom_message = cls._default_messages[MessageType.SUC_USER_CREATE]
        return cls._build_message(MessageType.SUC_USER_CREATE, custom_message)

    @classmethod
    @enforce_parameter_types
    def success_login(cls, custom_message: str = None) -> bytes:
        """Build a successful login message."""
        if custom_message is None:
            custom_message = cls._default_messages[MessageType.SUC_LOGIN]
        return cls._build_message(MessageType.SUC_LOGIN, custom_message)

    @classmethod
    @enforce_parameter_types
    def success_logout(cls, new_name: str) -> bytes:
        """Build a successful login message."""
        return cls._build_message(MessageType.SUC_LOGOUT, new_name)

    @classmethod
    @enforce_parameter_types
    def send_all_clients(cls, names: list[str]) -> bytes:
        """Sends a list of all connected client names."""
        return cls._build_message(MessageType.INFO_CLIENT_LIST, *names)

    @classmethod
    @enforce_parameter_types
    def send_client_connect(cls, user_name: str) -> bytes:
        """Send a client has connected message."""
        return cls._build_message(MessageType.INFO_CLIENT_CONN, user_name)

    @classmethod
    @enforce_parameter_types
    def send_client_disconnect(cls, user_name: str) -> bytes:
        """Send a client has disconnected message."""
        return cls._build_message(MessageType.INFO_CLIENT_DISC, user_name)

    @classmethod
    @enforce_parameter_types
    def send_client_update(cls, old_name: str, new_name: str) -> bytes:
        """Send updated client information."""
        return cls._build_message(MessageType.INFO_CLIENT_UPDATE, old_name, new_name)

    @classmethod
    @enforce_parameter_types
    def send_server_message(cls, message: str) -> bytes:
        """Build a server message."""
        return cls._build_message(MessageType.SVR_MESSAGE, message)

    @classmethod
    @enforce_parameter_types
    def send_whisper(cls, from_user: str, message: str) -> bytes:
        """Builds a whisper from message. Used by the server."""
        return cls._build_message(MessageType.SVR_CLIENT_WHISPER, from_user, message)

    @classmethod
    @enforce_parameter_types
    def send_say(cls, from_user: str, message: str) -> bytes:
        """Builds a whisper from message. Used by the server."""
        return cls._build_message(MessageType.SVR_CLIENT_SAY, from_user, message)

    #TODO: pass in the buffer_size?
    @classmethod
    @enforce_parameter_types
    def _build_message(cls, message_type: MessageType, *args: Tuple[str, ...]) -> bytes:
        """Constructs bytes based on message type provided.
        
        Args:
            message_type: MessageId describing how the message should be handled.
            *args: Variable length of strings to append to the message.

        Raises:
            ValueError if any message is too long.

        Returns:
            Formatted bytes.
        """
        total_length: int = Message.HEADER_LEN

        for arg in args:
            l = len(arg)
            if l < 1:
                continue
            # String length + 1 null byte separator
            total_length += l + 1
        # Pad the message to a multiple of BUFFER_MIN
        #TODO: BUFFER_MIN could be different from connection.py
        #put buffer min in connection and don't allow custom buff size in recv?
        padding = BUFFER_MIN - (total_length % BUFFER_MIN)
        total_length += padding

        # Build the header: type, length, timestamp, id
        b: bytearray = bytearray()
        b.append(cls.as_bytes(message_type))
        b.extend(total_length.to_bytes(Message.SIZE_FLD_LEN, byteorder='big', signed=False))
        b.extend(struct.pack('d', time.time()))
        b.extend(cls._message_counter.to_bytes(Message.ID_FLD_LEN, byteorder='big', signed=False))

        # Increment message counter and mask to a uint16
        cls._message_counter = (cls._message_counter + 1) & MSG_COUNTER_MASK

        # Append the data with null terminators
        for arg in args:
            b.extend(arg.encode('utf-8'))
            b.append(int.from_bytes(b'\x00', 'big'))
        # Add the padding
        for _ in range(0, padding):
            b.append(int.from_bytes(b'\x00', 'big'))
        print('returning bytes from build message')
        print(b.hex())
        print(bytes(b).hex())
        return bytes(b)

    @classmethod
    @enforce_parameter_types
    def parse_message(cls, data: bytes) -> Message:
        """Parses a message.

        Args:
            data: The bytes to parse.

        Returns:
            Message object.
        """
        # Get the time the message was received (technically parsed but close enough)
        time_recv: float = time.time()
        # Parse the message type
        message_type: MessageType = MessageType(data[:Message.TYPE_FLD_LEN])
        # Remove the message id bytes
        data = data[Message.TYPE_FLD_LEN:]
        # Parse the message length
        message_len = data[:Message.SIZE_FLD_LEN]
        message_len = int.from_bytes(message_len, 'big')
        # Remove the message length bytes
        data = data[Message.SIZE_FLD_LEN:]
        #Parse the time sent bytes
        time_sent = data[:Message.TIME_FLD_LEN]
        time_sent = struct.unpack('d', time_sent)
        # Remove the time sent bytes
        data = data[Message.TIME_FLD_LEN:]
        # Parse the id bytes
        message_id = data[:Message.ID_FLD_LEN]
        # Remove the id bytes
        data = data[Message.ID_FLD_LEN:]
        # Store the parsed strings
        fields: list[str] = []

        # Get how many bytes SHOULD be remaining base on the message length field
        bytes_left = message_len - Message.HEADER_LEN
        # Decode the bytes into strings separated by null bytes
        string: bytearray = bytearray()

        for _, b in enumerate(data):
            bytes_left -= 1
            if b == 0x00:
                if len(string) > 0:
                    fields.append(string.decode('utf-8'))
                    string.clear()
            else:
                string.append(b)

        is_malformed: bool = bytes_left != 0

        return Message(message_type,
                       bytes_left,
                       time_recv,
                       time_sent,
                       message_id,
                       fields,
                       is_malformed)
