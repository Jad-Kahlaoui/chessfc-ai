from typing import Optional

from .client import Client, ClientOption, ServerOption, PlayerCallbacks
from .player_types import StartFn, StrategyFn, FinalFn


def start(
        start_fn: StartFn,
        strategy_fn: StrategyFn,
        final_fn: FinalFn,
        client_option: Optional[ClientOption] = None,
        server_option: Optional[ServerOption] = None,
) -> None:
    """
    Start the communication loop with the server

    Args:
        start_fn (StartFn): Function called before starting a match
        strategy_fn (StrategyFn): Function called each turn
        final_fn (FinalFn): Function called at the end of the match
        client_option (Optional[ClientOption]): Client's options
        server_option (Optional[ServerOption]): Server's options

    Returns:
        None
    """
    player_callbacks = PlayerCallbacks(
        start_fn,
        strategy_fn,
        final_fn,
    )
    if client_option is None:
        client_option = ClientOption()

    if server_option is None:
        server_option = ServerOption()

    client = Client(player_callbacks, client_option, server_option)
    client.run()
