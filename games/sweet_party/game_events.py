SPAWN_X_TILE = "spawnXTile"


def spawn_x_tile_event(gamestate) -> None:
    """Emit the Gold X-Tile position to the book for front-end rendering.
    No-ops if no X-Tile spawned this spin."""
    if gamestate.x_tile_position is None:
        return
    event = {
        "index": len(gamestate.book.events),
        "type": SPAWN_X_TILE,
        "position": {
            "reel": gamestate.x_tile_position[0],
            "row": gamestate.x_tile_position[1],
        },
    }
    gamestate.book.add_event(event)
