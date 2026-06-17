from dataclasses import dataclass
from enum import Enum
from typing import Optional


class PlayerRole(Enum):
    WHITE = 0
    BLACK = 1
    NONE = 2


Duration = int


@dataclass
class Coord:
    x: int
    y: int


@dataclass
class Action:
    from_cell: Coord
    to_cell: Coord


MaybeAction = Optional[Action]
MaybeMaybeAction = Optional[tuple[MaybeAction, MaybeAction]]

Score = float


class Piece(Enum):
    EMPTY = 0
    ROOK = 1
    KNIGHT = 2
    BISHOP = 3
    PAWN = 4
    QUEEN = 5


@dataclass
class Team:
    pieces: tuple[Coord, Coord, Coord, Coord, Coord, Coord]
    captured: int
    pawns_info: int


@dataclass
class Board:
    board: tuple[tuple[tuple[Piece, PlayerRole, bool], ...], ...]
    en_passant: tuple[Coord, ...]


@dataclass
class State:
    board: Board
    current_player: PlayerRole
    current_turn: int


DEFAULT_STATE = (
    (
        (Piece.EMPTY, PlayerRole.NONE, False),
        (Piece.EMPTY, PlayerRole.NONE, False),
        (Piece.EMPTY, PlayerRole.NONE, False),
        (Piece.EMPTY, PlayerRole.NONE, False),
        (Piece.EMPTY, PlayerRole.NONE, False),
        (Piece.EMPTY, PlayerRole.NONE, False),
        (Piece.EMPTY, PlayerRole.NONE, False),
        (Piece.EMPTY, PlayerRole.NONE, False),
        (Piece.EMPTY, PlayerRole.NONE, False),
    ),
    (
        (Piece.EMPTY, PlayerRole.NONE, False),
        (Piece.EMPTY, PlayerRole.NONE, False),
        (Piece.EMPTY, PlayerRole.NONE, False),
        (Piece.EMPTY, PlayerRole.NONE, False),
        (Piece.EMPTY, PlayerRole.NONE, False),
        (Piece.EMPTY, PlayerRole.NONE, False),
        (Piece.EMPTY, PlayerRole.NONE, False),
        (Piece.EMPTY, PlayerRole.NONE, False),
        (Piece.EMPTY, PlayerRole.NONE, False),
    ),
    (
        (Piece.ROOK, PlayerRole.WHITE, False),
        (Piece.PAWN, PlayerRole.WHITE, False),
        (Piece.EMPTY, PlayerRole.NONE, False),
        (Piece.EMPTY, PlayerRole.NONE, False),
        (Piece.EMPTY, PlayerRole.NONE, False),
        (Piece.EMPTY, PlayerRole.NONE, False),
        (Piece.EMPTY, PlayerRole.NONE, False),
        (Piece.PAWN, PlayerRole.BLACK, False),
        (Piece.KNIGHT, PlayerRole.BLACK, False),
    ),
    (
        (Piece.BISHOP, PlayerRole.WHITE, False),
        (Piece.PAWN, PlayerRole.WHITE, False),
        (Piece.EMPTY, PlayerRole.NONE, False),
        (Piece.EMPTY, PlayerRole.NONE, False),
        (Piece.EMPTY, PlayerRole.NONE, True),
        (Piece.EMPTY, PlayerRole.NONE, False),
        (Piece.EMPTY, PlayerRole.NONE, False),
        (Piece.PAWN, PlayerRole.BLACK, False),
        (Piece.BISHOP, PlayerRole.BLACK, False),
    ),
    (
        (Piece.KNIGHT, PlayerRole.WHITE, False),
        (Piece.PAWN, PlayerRole.WHITE, False),
        (Piece.EMPTY, PlayerRole.NONE, False),
        (Piece.EMPTY, PlayerRole.NONE, False),
        (Piece.EMPTY, PlayerRole.NONE, False),
        (Piece.EMPTY, PlayerRole.NONE, False),
        (Piece.EMPTY, PlayerRole.NONE, False),
        (Piece.PAWN, PlayerRole.BLACK, False),
        (Piece.ROOK, PlayerRole.BLACK, False),
    ),
    (
        (Piece.EMPTY, PlayerRole.NONE, False),
        (Piece.EMPTY, PlayerRole.NONE, False),
        (Piece.EMPTY, PlayerRole.NONE, False),
        (Piece.EMPTY, PlayerRole.NONE, False),
        (Piece.EMPTY, PlayerRole.NONE, False),
        (Piece.EMPTY, PlayerRole.NONE, False),
        (Piece.EMPTY, PlayerRole.NONE, False),
        (Piece.EMPTY, PlayerRole.NONE, False),
        (Piece.EMPTY, PlayerRole.NONE, False),
    ),
    (
        (Piece.EMPTY, PlayerRole.NONE, False),
        (Piece.EMPTY, PlayerRole.NONE, False),
        (Piece.EMPTY, PlayerRole.NONE, False),
        (Piece.EMPTY, PlayerRole.NONE, False),
        (Piece.EMPTY, PlayerRole.NONE, False),
        (Piece.EMPTY, PlayerRole.NONE, False),
        (Piece.EMPTY, PlayerRole.NONE, False),
        (Piece.EMPTY, PlayerRole.NONE, False),
        (Piece.EMPTY, PlayerRole.NONE, False),
    ),
)
