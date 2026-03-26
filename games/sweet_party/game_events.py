"""Game-specific events for Sweet Party."""

from src.events.event_constants import EventConstants


def xtile_spawn_event(gamestate) -> None:
    """Emit when a Gold X-Tile spawns on the board."""
    reel: int = gamestate.xtile_position[0]
    row: int = gamestate.xtile_position[1]
    if gamestate.config.include_padding:
        row += 1
    event: dict = {
        "index": len(gamestate.book.events),
        "type": EventConstants.XTILE_SPAWN.value,
        "position": {"reel": reel, "row": row},
    }
    gamestate.book.add_event(event)


def xtile_apply_event(gamestate, cluster_symbol: str, cluster_positions: list[dict[str, int]]) -> None:
    """Emit when a Gold X-Tile applies multipliers to a winning cluster."""
    event: dict = {
        "index": len(gamestate.book.events),
        "type": EventConstants.XTILE_APPLY.value,
        "clusterSymbol": cluster_symbol,
        "clusterPositions": cluster_positions,
    }
    gamestate.book.add_event(event)
