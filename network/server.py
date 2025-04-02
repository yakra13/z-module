"""12.6 In Python, demonstrate skill in using networking commands accounting for endianness
Objectives
- [x] sendto()
- [x] recvfrom()
- [x] bind()
- [x] listen()
- [x] connect()
- [x] accept()
- [x] close()
- [x] gethostname()
- [x] socket()
- [x] send() // sendall currently
- [x] recv()
"""
import signal
import socket
import threading
from _thread import LockType
from typing import Final
from concurrent.futures import Future, ThreadPoolExecutor
from concurrent.futures import as_completed

from z_module.network.connection import Connection
from z_module.network.message import Builder, Message, MessageType
from z_module.network.server_action import ServerActionManager
from z_module.network.server_sql_manager import LogType, SQLManager
from z_module.validation import Validate
from z_module.types.int import UInt16, UInt64
from z_module.validation import enforce_parameter_types
from z_module.network.types import _Connections

DEFAULT_TIMEOUT: Final[int] = 1
UDP_RECV_BUFFER_SIZE: Final[int] = 4


class Server():
    """A chat server."""
    DEFAULT_ADDRESS: Final[str]      = '127.0.0.1'
    DEFAULT_PORT: Final[int]         = 7777
    DEFAULT_SERVICE_PORT: Final[int] = 7778

    # @enforce_parameter_types
    def __init__(self,
                 address: str = DEFAULT_ADDRESS,
                 port: int = DEFAULT_PORT,
                 service_port: int = DEFAULT_SERVICE_PORT) -> None:

        Validate.start(address).is_ip_address()
        Validate.start(port).in_range(1, UInt16.MAX)
        Validate.start(service_port).in_range(1, UInt16.MAX)

        if port == service_port:
            raise ValueError('Server port and service_port must be different values.')

        self._address: str               = address
        self._server_port: int           = port
        self._manage_port: int           = service_port
        self._server_sock: socket.socket = None
        self._manage_sock: socket.socket = None

        self._tp_exec: ThreadPoolExecutor = ThreadPoolExecutor(max_workers=20) #TODO: test value
        self._tp_lock: LockType           = threading.Lock()

        self._is_running: bool        = False
        self._is_shut_down: bool      = False
        self._conns: _Connections     = {}
        self._message_of_the_day: str = 'This is the servers message of the day.'

        self._backlog: int            = 18 # TODO: testing value
        self._hostname: str           = socket.gethostname()
        self._connection_counter: int = 0
        self._buffer_size: UInt64     = Connection.DEFAULT_BUFF_SIZE

        self._sql_manager: SQLManager             = SQLManager()
        self._action_manager: ServerActionManager = ServerActionManager(self._sql_manager)

        self._futures: list[Future] = []

    def _signal_handler(self, signum, frame):
        """Handles ctrl+c to shutdown the server."""
        print(f'DEBUG: Closing connections and shutting down.\n{signum} {frame}')
        self._is_shut_down = True

    def run(self) -> None:
        """Start the server."""
        if self._is_running:
            return

        # Setup ctrl+c intercept
        signal.signal(signal.SIGINT, self._signal_handler)

        self._is_running = True
        self._is_shut_down = False

        self._server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_sock.settimeout(DEFAULT_TIMEOUT)
        self._server_sock.bind((self._address, self._server_port))
        self._server_sock.listen(self._backlog)

        main_thread_future = self._tp_exec.submit(self._run)

        # Start the UDP based management thread
        # manager_future = self._tp_exec.submit(self._run_manager_service)

        self._futures.append(main_thread_future)
        # self._futures.append(manager_future)

        for future in as_completed(self._futures):
            future.result()

    def _run(self) -> None:
        """Start the server."""
        while True:
            if self._is_shut_down:
                break

            try:
                client, addr = self._server_sock.accept()
                client.settimeout(DEFAULT_TIMEOUT)

                temp_name = 'user_' + str(self._connection_counter).zfill(5)
                new_conn = Connection(sock=client,
                                      address=addr[0],
                                      port=UInt16(int(addr[1])),
                                      user_name=temp_name,
                                      buffer_size=self._buffer_size,
                                      tp_lock=self._tp_lock)
                new_conn.is_connected = True

                self._sql_manager.add_new_log(LogType.INFO, f'{addr} connected')

                self._tp_lock.acquire()

                self._conns[temp_name] = new_conn
                self._action_manager.broadcast_client_connect(new_conn, self._conns)
                self._connection_counter += 1

                future = self._tp_exec.submit(self._handle_client, self._conns[temp_name])
                self._futures.append(future)

                self._tp_lock.release()
            except InterruptedError as err:
                print(f'DEBUG: interrupt error: {err}')
                break
            except socket.timeout:
                self._tp_lock.acquire()
                for _, c in self._conns.items():
                    self._process_message_queue(c)
                self._tp_lock.release()
                continue
            except OSError as err:
                print(f'DEBUG: OS Error on accept: {err}')
                break
            finally:
            #     # Check status of the management service and restart it if it died
            #     try:
            #         if self._manager_future.result(0.5):
            #             self._manage_sock.close()
            #             self._manager_future = self._tp_exec.submit(self._run_manager_service)
            #     except cf_TimeoutError:
                continue

        self._shutdown()
        return

    @enforce_parameter_types
    def _process_message_queue(self, conn: Connection) -> None:
        """"""
        msg: Message = None
        while (msg := conn.message_queue.pop()) is not None:
            if msg.is_malformed:
                conn.send_bytes(Builder.error_malformed_data())
                continue

            match msg.type:
                case MessageType.REQ_CREATE_USER:
                    self._req_user_create(msg, conn)

                case MessageType.REQ_LOGIN:
                    self._req_login(msg, conn)

                case MessageType.REQ_LOGOUT:
                    self._req_logout(conn)

                case MessageType.REQ_DISCONNECT:
                    self._req_disconnect(conn)

                case MessageType.REQ_SAY:
                    self._req_say(msg, conn)

                case MessageType.REQ_WHISPER:
                    self._req_whisper(msg, conn)

                case _:
                    print(conn.user_name, 'request _')
                    # TODO:
                    # self._sql_manager.add_new_log(f'Type not implemented: {m.type}', True)
                    conn.send_bytes(Builder.error_generic('Unsupported message type.'))

    @enforce_parameter_types
    def _handle_client(self, conn: Connection) -> None:
        """Thread function to handle each connection."""
        print('start handling client')
        with self._tp_lock:
            print(conn.user_name, 'client connected...', conn)
            # Send success connection containing temporary user name
            # conn.send_bytes(Builder.success_connect(conn.name))
            # Send MotD
            print('send motd')
            # conn.send_bytes(Builder.send_server_message(self._message_of_the_day))
            # Update this client with currently connected clients
            print('send all connections')
            self._action_manager.send_connections(conn, self._conns)
        print('start handle loop')
        while True:
            print('wait for data')
            with self._tp_lock:
                if conn.is_closing is True:
                    print('conn is closing in handle client')
                    break

                data: bytes = conn.recv_bytes()
                if not data:
                    print('not data start process queue')
                    #there should be at least 1 message in the queue
                    # self._process_message_queue(conn)
                    #TODO: The client recv timed out. This is ok.
                    # Do any additional logic here like increasing the timeout
                    # or sending a heartbeat request.
                    continue
                else:
                    print(data.hex())

        print('end handle loop')
        self._on_client_disconnect(conn)

    @enforce_parameter_types
    def _on_client_disconnect(self, conn: Connection) -> None:
        """Closes a specified connection."""
        # Update other clients of the disconnecting client
        print('on client disconnect')
        self._action_manager.broadcast_client_disconnect(conn, self._conns)

        conn.close_connection()
        del self._conns[conn.user_name]

    def _close_connections(self) -> None:
        """Closes all connections."""
        if not self._is_running:
            return

        message: str = '\nServer closing...'
        for _, v in self._conns.items():
            v.socket.send(Builder.send_server_message(message))
            v.shutdown = True

    def _run_manager_service(self) -> None:
        """Runs the server management service as UDP(For example purposes. TCP Future)."""
        self._manage_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._manage_sock.settimeout(DEFAULT_TIMEOUT)
        self._manage_sock.bind((self._address, self._server_port))

        #TODO Future remote server management.
        while True:
            # Check if we should stop running this thread during a shutdown

            if self._is_shut_down:
                break

            try:
                data, address = self._manage_sock.recvfrom(UDP_RECV_BUFFER_SIZE)
            except InterruptedError:
                #TODO log error
                break
            except socket.timeout:
                #TODO Future any actions to complete between time outs
                continue
            except OSError:
                #TODO log error
                break
            #TODO Future this is just a test and will be replaced
            print(f"[UDP] {address} = {data.decode('utf-8')}", True)

            reply = "Yea sure sounds good. Thanks bro."
            self._manage_sock.sendto(reply.encode('utf-8'), address)

    def _shutdown(self) -> None:
        """Shuts down the server closing any active connections."""
        self._close_connections()
        self._is_running = False
        self._is_shut_down = False
        self._tp_exec.shutdown(wait=True, cancel_futures=True)

        #TODO: log shutdown
        # self._sql_manager.add_new_log('Successfully shutdown.', True)

    def _req_user_create(self, message: Message, conn: Connection) -> None:
        print(conn.user_name, 'request create user')
        try:
            user: str = message.get_next_field()
            pswd: str = message.get_next_field()
        except IndexError as err:
            conn.send_bytes(Builder.error_malformed_data(err))
            return
        conn.send_bytes(self._action_manager.create_user(user, pswd))

    def _req_login(self, message: Message, conn: Connection) -> None:
        print(conn.user_name, 'request login')
        try:
            user: str = message.get_next_field()
            pswd: str = message.get_next_field()
        except IndexError as err:
            conn.send_bytes(Builder.error_malformed_data(err))
            return
        # Store the name so on we can update the other clients of the name change
        old_name: str = conn.name
        conn.send_bytes(self._action_manager.login_user(conn, user, pswd, self._conns))
        # Update other clients of the new name
        if conn.is_logged_in:
            self._action_manager.broadcast_client_update(old_name, conn, self._conns)

    def _req_logout(self, conn: Connection) -> None:
        print(conn.user_name, 'request logout')
        old_name: str = conn.user_name
        conn.user_name = 'user_' + str(self._connection_counter).zfill(5)
        self._connection_counter += 1
        conn.is_logged_in = False
        self._action_manager.broadcast_client_update(old_name, conn, self._conns)
        conn.send_bytes(Builder.success_logout(conn.name))

    def _req_disconnect(self, conn: Connection) -> None:
        # The client is letting the server know it is disconnecting.
        #TODO self._sql_manager.add_new_log(conn req disc)
        print(conn.user_name, 'request disconnect')
        # Exit the while loop and  handle the disconnect process.
        conn.close_connection()

    def _req_say(self, message: Message, conn: Connection) -> None:
        print(conn.user_name, 'request say')
        try:
            say: str = message.get_next_field()
        except IndexError as err:
            conn.send_bytes(Builder.error_malformed_data(err))
            return

        say: str = f'{conn.name} says: {say}'
        self._action_manager.broadcast(say, self._conns, [conn.name])

        if conn.logged_in:
            #TODO: log in sql
            # self._sql_manager.add_new_user_history(user, message, type etc)
            pass

    def _req_whisper(self, message: Message, conn: Connection) -> None:
        print(conn.user_name, 'request whisper')
        try:
            user: str    = message.get_next_field()
            whisper: str = message.get_next_field()
        except IndexError as err:
            conn.send_bytes(Builder.error_malformed_data(err))
            return

        try:
            self._action_manager.whisper(self._conns[user], conn, whisper)
        except socket.error:
            #TODO have no idea what specific exception it would be
            # maybe if the conn is no longer in the dictionary?
            conn.send_bytes(Builder.error_user_offline())
            return

        if conn.logged_in:
            #TODO: log in sql
            conn.log_message(f'[WHISPER]({user}) {whisper}')

        conn.send_bytes(Builder.success_generic('Whisper received.'))
