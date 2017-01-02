import hlt
from hlt import NORTH, EAST, SOUTH, WEST, STILL, Move

myID, game_map = hlt.get_init()
hlt.send_init("MyPythonBot")


def find_nearest_enemy_direction(square):
    """
    Identify closest enemy direction/location
    :param square: Map location for move
    :return: Direction of closest enemy
    """

    direction = NORTH
    max_distance = min(game_map.width, game_map.height) / 2
    for d in (NORTH, EAST, SOUTH, WEST):
        distance = 0
        current = square
        while current.owner == myID and distance < max_distance:
            distance += 1
            current = game_map.get_target(current, d)
        if distance < max_distance:
            direction = d
            max_distance = distance
    return direction


def heuristic(square):
    """
    Calculate optimal movement heuristic
    :param square: Map location for move
    :return: Total potential offense damage
    """

    if square.owner == 0 and square.strength > 0:
        return square.production / square.strength
    else:
        # Total potential damage caused by overkill when attacking this square
        return sum(neighbor.strength for neighbor in game_map.neighbors(square) if neighbor.owner not in (0, myID))


# Maximum 1 second
def get_move(square):
    """
    Return move for square - NORTH, SOUTH, WEST, EAST, STILL
    :param square: Map location for move
    :return: NORTH, SOUTH, WEST, EAST, STILL
    """

    target, direction = max(((neighbor, direction) for direction, neighbor in enumerate(game_map.neighbors(square))
                             if neighbor.owner != myID), default=(None, None), key=lambda t: heuristic(t[0]))

    if target is not None and target.strength < square.strength:
        return Move(square, direction)

    elif square.strength < square.production * 5:
        return Move(square, STILL)

    border = any(neighbor.owner != myID for neighbor in game_map.neighbors(square))
    if not border:
        return Move(square, find_nearest_enemy_direction(square))

    # Wait till strong enough to attack
    return Move(square, STILL)


while True:
    game_map.get_frame()
    moves = [get_move(_square) for _square in game_map if _square.owner == myID]
    hlt.send_frame(moves)
