from typing import Optional, Self
from .game import Action, MaybeAction

Response = str

PLAYER_RESPONSE_READY: Response = "( ready )"
PLAYER_RESPONSE_AVAILABLE: Response = "( available )"
PLAYER_RESPONSE_BUSY: Response = "( busy )"
PLAYER_RESPONSE_NOOP: Response = "( noop )"
PLAYER_RESPONSE_DONE: Response = "( done )"


def x_to_char(x: int) -> str:
    return chr(ord("A") + x - 1)


class ResponseBuilder:
    def __init__(self: Self) -> None:
        self.action: MaybeAction = None

    def set_maybe_action(self: Self, action: Optional[Action] = None) -> Self:
        self.action = action
        return self

    def ready(self: Self) -> Response:
        return PLAYER_RESPONSE_READY

    def available(self: Self) -> Response:
        return PLAYER_RESPONSE_AVAILABLE

    def busy(self: Self) -> Response:
        return PLAYER_RESPONSE_BUSY

    def noop(self: Self) -> Response:
        return PLAYER_RESPONSE_NOOP

    def done(self: Self) -> Response:
        return PLAYER_RESPONSE_DONE

    def move(self: Self) -> Response:
        match self.action:
            case None:
                return self.noop()
            case Action(from_cell, to_cell):
                return Response(
                    f"( move {x_to_char(from_cell.x)} {from_cell.y} {
                        x_to_char(to_cell.x)
                    } {to_cell.y})"
                )
            case _:
                raise ValueError
