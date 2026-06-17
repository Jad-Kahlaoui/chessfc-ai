from enum import Enum
from typing import Any, Callable, Optional, Mapping, Self

from .game import Action, Duration, MaybeMaybeAction, PlayerRole, Score, State

Environment = Optional[Mapping[str, Any]]
StartFn = Callable[
    [
        str,
        Environment,
        PlayerRole,
        Duration,
        Duration,
        Duration,
        int,
        State,
        MaybeMaybeAction,
    ],
    Environment,
]
StrategyFn = Callable[
    [str, Environment, State, MaybeMaybeAction, PlayerRole, Duration],
    tuple[Action, Environment],
]
FinalFn = Callable[
    [str, Environment, State, MaybeMaybeAction, Score, PlayerRole, Duration], None
]


class ClientOption:
    def __init__(
        self: Self,
        host: str = "127.0.0.1",
        port: str = "0",
        name: str = "python-client",
    ) -> None:
        """
        Create a ClientObject object

        Args:
            host (str): client's ip address
            port (str): client's port
            name (str): client's name

        Returns:
            None
        """
        self.host = host
        self.port = port
        self.name = name


class ServerOption:
    def __init__(
        self: Self,
        host: str = "127.0.0.1",
        port: str = "8080",
        service: str = "/ws",
    ) -> None:
        """
        Create a ServerOption object

        Args:
            host (str): server's ip address
            port (str): server's port
            service (str): server's connection service

        Returns:
            None
        """
        self.host = host
        self.port = port
        self.service = service


class NewMatchBehaviour(Enum):
    PASS_NONE = 0
    PASS_LAST_ENVIRONMENT = 1
    PASS_FIRST_ENVIRONMENT = 2
