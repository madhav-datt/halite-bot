from networking import *
import os
import sys
import numpy as np

VISIBLE_DISTANCE = 4
input_dim=4*(2*VISIBLE_DISTANCE+1)*(2*VISIBLE_DISTANCE+1)

myID, gameMap = getInit()
game_map = gameMap

with open(os.devnull, 'w') as sys.stderr:
    from keras.models import load_model
    model = load_model('model-20.h5')

model.predict(np.random.randn(1,input_dim)).shape  # make sure model is compiled during init


def stack_to_input(stack, position):
    return np.take(np.take(stack,
                np.arange(-VISIBLE_DISTANCE,VISIBLE_DISTANCE + 1)+position[0],axis=1,mode='wrap'),
                np.arange(-VISIBLE_DISTANCE,VISIBLE_DISTANCE + 1)+position[1],axis=2,mode='wrap').flatten()


def frame_to_stack(frame):
    game_map = np.array([[(x.owner, x.production, x.strength) for x in row] for row in frame.contents])
    return np.array([(game_map[:, :, 0] == myID),  # 0 : owner is me
                      ((game_map[:, :, 0] != 0) & (game_map[:, :, 0] != myID)),  # 1 : owner is enemy
                      game_map[:, :, 1]/20,  # 2 : production
                      game_map[:, :, 2]/255,  # 3 : strength
                      ]).astype(np.float32)


def find_nearest_enemy_direction(square):
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
    if square.owner == 0 and square.strength > 0:
        return square.production / square.strength
    else:
        # return total potential damage caused by overkill when attacking this square
        return sum(neighbor.strength for neighbor in game_map.neighbors(square) if neighbor.owner not in (0, myID))


# Maximum 1 second
def get_move(square):
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

sendInit('brianvanleeuwen')
while True:
    stack = frame_to_stack(getFrame())
    positions = np.transpose(np.nonzero(stack[0]))
    output = model.predict(np.array([stack_to_input(stack, p) for p in positions]))

    # Manual output corrections to avoid obviously bad moves

    sendFrame([Move(Location(positions[i][1], positions[i][0]), output[i].argmax()) for i in range(len(positions))])
