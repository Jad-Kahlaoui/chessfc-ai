from enum import Enum
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
    State,
    Board,
    Piece,
    Team,
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

    state: State

    actions: MaybeMaybeAction


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


def parse_team(tokens: Iterator[str]) -> Team:
    pieces = (
        Coord(parse_x(next(tokens)), int(next(tokens))),
        Coord(parse_x(next(tokens)), int(next(tokens))),
        Coord(parse_x(next(tokens)), int(next(tokens))),
        Coord(parse_x(next(tokens)), int(next(tokens))),
        Coord(parse_x(next(tokens)), int(next(tokens))),
        Coord(parse_x(next(tokens)), int(next(tokens))),
    )
    return Team(pieces, int(next(tokens)), int(next(tokens)))


class ServerPiece(Enum):
    ROOK = 0
    BISHOP = 1
    KNIGHT = 2
    PAWN = 3
    QUEEN = 4


server_to_client_pieces = (
    Piece.ROOK,
    Piece.BISHOP,
    Piece.KNIGHT,
    Piece.PAWN,
    Piece.QUEEN,
)


def parse_board(tokens: Iterator[str]) -> Board:
    white = parse_team(tokens)
    black = parse_team(tokens)
    ball = Coord(parse_x(next(tokens)), int(next(tokens)))

    board_list = [
        [(Piece.EMPTY, PlayerRole.NONE, False) for _ in range(9)] for _ in range(7)
    ]
    board_en_passant: list[Coord] = []

    for team, role in [(white, PlayerRole.WHITE), (black, PlayerRole.BLACK)]:
        for idx, piece in enumerate(team.pieces):
            if team.captured & (1 << idx) == 0:
                piece_idx: int
                if idx >= ServerPiece.PAWN.value:
                    if team.pawns_info & (1 << (idx - ServerPiece.PAWN.value + 3)) != 0:
                        piece_idx = ServerPiece.QUEEN.value
                    else:
                        if team.pawns_info & (1 << (idx - ServerPiece.PAWN.value)) != 0:
                            board_en_passant.append(piece)
                        piece_idx = ServerPiece.PAWN.value
                else:
                    piece_idx = idx

                board_list[piece.y - 1][piece.x - 1] = (
                    server_to_client_pieces[piece_idx],
                    role,
                    False,
                )

    board_list[ball.y - 1][ball.x - 1] = (
        board_list[ball.y - 1][ball.x - 1][0],
        board_list[ball.y - 1][ball.x - 1][1],
        True,
    )

    return Board(
        tuple(tuple(line) for line in board_list),
        tuple(board_en_passant),
    )


def parse_state(tokens: Iterator[str]) -> State:
    return State(
        parse_board(tokens),
        parse_role(tokens),
        int(next(tokens)),
    )


def parse_start(tokens: Iterator[str]) -> StartInfo:
    game_id: str = next(tokens)
    role = parse_role(tokens)
    start_clock = Duration(next(tokens))
    play_clock = Duration(next(tokens))
    total_clock = Duration(next(tokens))
    limit_turn_number = int(next(tokens))
    state = parse_state(tokens)
    actions = parse_maybe_maybe_action(tokens)

    return StartInfo(
        game_id,
        role,
        start_clock,
        play_clock,
        total_clock,
        limit_turn_number,
        state,
        actions,
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


def parse_maybe_maybe_action(tokens: Iterator[str]) -> MaybeMaybeAction:
    match token := next(tokens):
        case "nil":
            return None
        case "(":
            action_white = parse_inner_play_syntax(tokens)
            if (token := next(tokens)) != "(":
                raise InvalidRequestTokenError(token)
            action_black = parse_inner_play_syntax(tokens)
            return (action_white, action_black)

        case _:
            raise InvalidRequestTokenError(token)


def parse_play(tokens: Iterator[str]) -> PlayInfo:
    game_id: str = next(tokens)
    player_clock = Duration(next(tokens))
    actions = parse_maybe_maybe_action(tokens)
    return PlayInfo(game_id, player_clock, actions)


def parse_stop(tokens: Iterator[str]) -> StopInfo:
    game_id: str = next(tokens)
    score = Score(next(tokens))
    player_clock = Duration(next(tokens))
    actions = parse_maybe_maybe_action(tokens)

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
