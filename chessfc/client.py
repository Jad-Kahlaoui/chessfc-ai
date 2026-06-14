from collections import deque
from dataclasses import dataclass
from socket import create_connection
import threading
from typing import Self, TypeVar, Generic, Optional, Never
from websockets.sync.client import connect, Connection
from websockets.exceptions import ConnectionClosed

from .response import ResponseBuilder, Response
from .request import (
    RequestInfo,
    InfoInfo,
    StartInfo,
    PlayInfo,
    StopInfo,
    AbortInfo,
    parse_request,
)
from .game import (
    PlayerRole,
    State,
    Action,
    Piece,
    DEFAULT_STATE,
)
from .player_types import (
    StartFn,
    StrategyFn,
    FinalFn,
    Environment,
    ClientOption,
    ServerOption,
)

T = TypeVar("T")


@dataclass
class ServerInfo:
    host: str
    port: str
    service: str


class SendOnCloseChannel(ValueError):
    pass


class Channel(Generic[T]):
    def __init__(
        self: Self,
        buffer_size: int = 0,
    ) -> None:
        self.queue = deque[T]()
        self.buffer_size = max(buffer_size, 0)
        self.cond = threading.Condition()
        self.closed: bool = False
        self.reader: int = 0

    def send(self, data: T, blocking: bool = True) -> bool:
        with self.cond:
            if self.closed:
                raise SendOnCloseChannel()

            if self.buffer_size == 0:
                if not self.queue:
                    if blocking or self.reader > 0:
                        self.queue.append(data)
                        self.cond.notify_all()
                    else:
                        return False
                else:
                    if blocking:
                        while self.queue:
                            self.cond.wait()
                        self.queue.append(data)
                        self.cond.notify_all()
                    else:
                        return False
            else:
                if len(self.queue) < self.buffer_size:
                    self.queue.append(data)
                    self.cond.notify_all()
                elif blocking:
                    while len(self.queue) >= self.buffer_size:
                        self.cond.wait()
                    self.queue.append(data)
                    self.cond.notify_all()
                else:
                    return False

            return True

    def __can_read(self: Self) -> bool:
        return len(self.queue) > 0 or self.closed

    def close(self: Self) -> None:
        with self.cond:
            self.closed = True
            self.cond.notify_all()

    def recv(self: Self, blocking: bool = True) -> Optional[T]:
        with self.cond:
            if blocking or (not blocking and self.__can_read()):
                self.reader += 1
                while not self.queue and not self.closed:
                    self.cond.wait()

                if self.closed:
                    item = None
                    if self.queue:
                        item = self.queue.popleft()
                    self.reader -= 1
                    return item

                item = self.queue.popleft()
                self.reader -= 1
                self.cond.notify_all()
                return item

            return None


class Mutex(Generic[T]):
    def __init__(self: Self, item: T) -> None:
        self.item: T = item
        self.cond = threading.Lock()

    def set(self, data: T) -> None:
        with self.cond:
            self.item = data

    def get(self: Self) -> T:
        with self.cond:
            return self.item


@dataclass
class PlayerCallbacks:
    start_fn: StartFn
    strategy_fn: StrategyFn
    final_fn: FinalFn


class Client:
    def __init__(
        self: Self,
        player_callbacks: PlayerCallbacks,
        client_option: ClientOption,
        server_option: ServerOption,
    ) -> None:
        self.read_from = Channel[RequestInfo]()
        self.send_to = Channel[Response]()
        self.connection: Optional[Connection] = None

        self.host = client_option.host
        self.port = client_option.port
        self.name = client_option.name

        self.server_option = ServerInfo(
            host=server_option.host,
            port=server_option.port,
            service=server_option.service,
        )

        self.builder = ResponseBuilder()

        self.role = PlayerRole.NONE

        self.player_callbacks = player_callbacks
        self.environment: Environment = None

    def __read_pump(self: Self, status: Mutex[bool]) -> Never:
        while True:
            if self.connection is not None:
                data: str | bytes = self.connection.recv()
                if isinstance(data, str):
                    print(data)
                    request_info = parse_request(data)

                    if isinstance(request_info, InfoInfo):
                        if status.get():
                            self.send_to.send(self.builder.available())
                        else:
                            self.send_to.send(self.builder.busy())

                    else:
                        self.read_from.send(request_info)

    def __write_pump(self: Self) -> Never:
        while True:
            if self.connection is not None:
                data = self.send_to.recv()
                if data is not None:
                    self.connection.send(data)

    def __wait_for_info(self: Self, status: Mutex[bool]) -> None:
        status.set(True)

    def __wait_for_start(self: Self, status: Mutex[bool]) -> None:
        while True:
            request = self.read_from.recv()
            if isinstance(request, StartInfo):
                status.set(False)
                print(request)
                self.role = request.role

                self.environment = self.player_callbacks.start_fn(
                    request.game_id,
                    request.role,
                    request.start_clock,
                    request.play_clock,
                    request.total_clock,
                    request.limit_turn_number,
                )

                self.send_to.send(self.builder.ready())
                return

    def __play(self: Self, state: State, action: Action) -> State:
        action.from_cell.x -= 1
        action.from_cell.y -= 1
        action.to_cell.x -= 1
        action.to_cell.y -= 1
        list_state = [list(row) for row in state]
        piece, team, ball = state[action.from_cell.y][action.from_cell.x]
        to_piece, to_team, to_ball = state[action.to_cell.y][action.to_cell.x]

        if ball:
            list_state[action.from_cell.y][action.from_cell.x] = (
                piece, team, False)
            list_state[action.to_cell.y][action.to_cell.x] = (
                to_piece, to_team, True)
        else:
            list_state[action.from_cell.y][action.from_cell.x] = (
                Piece.EMPTY,
                PlayerRole.NONE,
                False,
            )
            list_state[action.to_cell.y][action.to_cell.x] = (
                piece, team, to_ball)

        return tuple(tuple(cell for cell in row) for row in list_state)

    def __wait_for_play(self: Self) -> None:
        print("play")
        turn = PlayerRole.WHITE.value
        state: State = DEFAULT_STATE
        while True:
            request = self.read_from.recv()
            print(request)

            if request is None:
                raise ValueError

            match request:
                case PlayInfo(
                    game_id=game_id, player_clock=player_clock, actions=actions
                ):
                    other_turn = (turn + 1) % 2

                    if actions is not None:
                        if actions[other_turn] is None or actions[turn] is not None:
                            raise ValueError(turn, actions)

                        previous_action = actions[other_turn]
                        if previous_action is None:
                            raise ValueError
                        state = self.__play(state, previous_action)

                    if turn == self.role.value:
                        action, new_environment = self.player_callbacks.strategy_fn(
                            game_id, self.environment, state, self.role, player_clock
                        )
                        self.builder.set_maybe_action(action)
                        self.environment = new_environment
                    else:
                        self.builder.set_maybe_action(None)

                    self.send_to.send(self.builder.move())

                    turn = other_turn
                    continue

                case StopInfo(
                    game_id=game_id,
                    score=score,
                    player_clock=player_clock,
                    actions=actions,
                ):
                    self.send_to.send(self.builder.done())
                    self.player_callbacks.final_fn(
                        game_id, self.environment, state, score, self.role, player_clock
                    )
                    return

                case AbortInfo(game_id):
                    return

    def __update(self: Self, status: Mutex[bool]) -> None:
        self.__wait_for_info(status)
        self.__wait_for_start(status)
        self.__wait_for_play()

    def __server_addr(self: Self) -> str:
        return f"ws://{self.server_option.host}:{self.server_option.port}{self.server_option.service}"

    def run(self: Self) -> None:
        with create_connection(
            address=(self.server_option.host, int(self.server_option.port)),
            source_address=(self.host, int(self.port)),
        ) as socket:
            with connect(
                self.__server_addr(),
                sock=socket,
                compression=None,
                additional_headers={
                    "Cookie": f"chess-fc-client-name={self.name}"},
            ) as connection:
                self.connection = connection

                status = Mutex[bool](False)

                threading.Thread(
                    target=self.__read_pump, daemon=True, args=[status]
                ).start()
                threading.Thread(target=self.__write_pump, daemon=True).start()

                self.__update(status)
