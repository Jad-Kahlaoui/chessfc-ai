from dataclasses import dataclass
from typing import Iterator, Self
from .game import (
    Score,
    Coord,
    Action,
    MaybeAction,
    MaybeMaybeAction,
    Duration,
    PlayerRole,
)


class InfoInfo:
    def __init__(self: Self):
        pass


@dataclass
class StartInfo:
    game_id: str

    role: PlayerRole

    start_clock: Duration
    play_clock: Duration
    total_clock: Duration

    limit_turn_number: int


@dataclass
class PlayInfo:
    game_id: str

    player_clock: Duration

    actions: MaybeMaybeAction


@dataclass
class StopInfo:
    game_id: str

    score: Score

    player_clock: Duration

    actions: MaybeMaybeAction


@dataclass
class AbortInfo:
    game_id: str


RequestInfo = InfoInfo | StartInfo | PlayInfo | StopInfo | AbortInfo


def tokenize(data: str) -> Iterator[str]:
    return (token for token in data.strip().split())


class InvalidRequestTokenError(ValueError):
    def __init__(self: Self, token: str) -> None:
        self.token = token


class InvalidRequestFormatError(ValueError):
    def __init__(self: Self) -> None:
        pass


def parse_role(tokens: Iterator[str]) -> PlayerRole:
    match token := next(tokens):
        case "white":
            return PlayerRole.WHITE
        case "black":
            return PlayerRole.BLACK
        case _:
            raise InvalidRequestTokenError(token)


def parse_start(tokens: Iterator[str]) -> StartInfo:
    game_id: str = next(tokens)
    role = parse_role(tokens)
    start_clock = Duration(next(tokens))
    play_clock = Duration(next(tokens))
    total_clock = Duration(next(tokens))
    limit_turn_number = int(next(tokens))

    return StartInfo(
        game_id, role, start_clock, play_clock, total_clock, limit_turn_number
    )


def parse_x(token: str) -> int:
    if len(token) > 1:
        raise ValueError

    rune = token[0]

    if rune < "A" or rune > "I":
        raise ValueError

    return ord(rune) - ord("A") + 1


def parse_move(tokens: Iterator[str]) -> MaybeAction:
    return Action(
        Coord(parse_x(next(tokens)), int(next(tokens))),
        Coord(parse_x(next(tokens)), int(next(tokens))),
    )


def parse_inner_play_syntax(tokens: Iterator[str]) -> MaybeAction:
    action: MaybeAction
    match token := next(tokens):
        case "move":
            action = parse_move(tokens)
        case "noop":
            action = None
        case _:
            raise InvalidRequestTokenError(token)

    if (token := next(tokens)) != ")":
        raise InvalidRequestTokenError(token)

    return action


def parse_play(tokens: Iterator[str]) -> PlayInfo:
    game_id: str = next(tokens)
    player_clock = Duration(next(tokens))
    actions: MaybeMaybeAction
    match token := next(tokens):
        case "nil":
            actions = None
        case "(":
            action_white = parse_inner_play_syntax(tokens)
            if (token := next(tokens)) != "(":
                raise InvalidRequestTokenError(token)
            action_black = parse_inner_play_syntax(tokens)
            actions = (action_white, action_black)

        case _:
            raise InvalidRequestTokenError(token)
    return PlayInfo(game_id, player_clock, actions)


def parse_stop(tokens: Iterator[str]) -> StopInfo:
    game_id: str = next(tokens)
    score = Score(next(tokens))
    player_clock = Duration(next(tokens))
    actions: MaybeMaybeAction
    match token := next(tokens):
        case "nil":
            actions = None
        case "(":
            action_white = parse_inner_play_syntax(tokens)
            if (token := next(tokens)) != "(":
                raise InvalidRequestTokenError(token)
            action_black = parse_inner_play_syntax(tokens)
            actions = (action_white, action_black)

        case _:
            raise InvalidRequestTokenError(token)

    return StopInfo(game_id, score, player_clock, actions)


def parse_abort(tokens: Iterator[str]) -> AbortInfo:
    return AbortInfo(next(tokens))


def parse_inner_syntax(tokens: Iterator[str]) -> RequestInfo:
    request: RequestInfo
    match token := next(tokens):
        case "info":
            request = InfoInfo()
        case "start":
            request = parse_start(tokens)
        case "play":
            request = parse_play(tokens)
        case "stop":
            request = parse_stop(tokens)
        case "abort":
            request = parse_abort(tokens)
        case _:
            raise InvalidRequestTokenError(token)

    return request


def parse_syntax(tokens: Iterator[str]) -> RequestInfo:
    if (token := next(tokens)) != "(":
        raise InvalidRequestTokenError(token)

    request = parse_inner_syntax(tokens)

    if (token := next(tokens)) != ")":
        raise InvalidRequestTokenError(token)

    try:
        next(tokens)
    except StopIteration:
        return request

    raise InvalidRequestFormatError()


def parse_request(data: str) -> RequestInfo:
    tokens = tokenize(data)

    return parse_syntax(tokens)
