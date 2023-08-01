import threading

from Entities.Classes.Card import Card
from Entities.Classes.Player import Player
from Features.Game import Game
from Features.Detection import *
from Features.Statics import *
import time


def handle_actions():
    with lock:
        pending = actions

    money = 1.5 * ante

    while not (not pending and False):
        if pending:
            action, participant, ind = pending[0]

            match action:
                case "Call" | "Check":

                    pending.pop(0)
                    money += player.pay()
                    #participant.inRound = False

                    print("Player: " + str(ind) + " " + str(action))

                case "Fold":
                    pending.pop(0)
                    participant.set_ingame(False)
                    print("Player: " + str(ind) + " " + str(action))

                case "Raise" | "Bet" | "AllIn":

                    # Branch this
                    print("Player: " + str(ind) + " " + str(action))
                    #raised = float(input("Player: " + str(index) + " raised by? \n"))
                    raised = 1
                    pending.pop(0)
                    for opponent in [opponent for opponent in players if opponent.inGame]:
                        opponent.inRound = True
                        opponent.bet += raised

                    money += participant.pay()
                    # ----

                    #participant.inRound = False
        else:
            time.sleep(1)
            with lock:
                pending = actions


# Program settings
debug = True

# Config
config = ConfigParser()
config.read('AppConfig.ini')
runs = int(config["game"]["runs"])
# nr_of_players = int(config["game"]["nr_players"])
players_pos = [
    (928, 769, 1060, 801),
    (295, 581, 433, 613),
    (340, 264, 476, 296),
    (852, 168, 979, 197),
    (1444, 266, 1570, 297),
    (1486, 584, 1611, 614)
]
# ante = float(config["game"]["ante"])

# Set values
ante = 0.02
nr_of_players = 6
if debug:
    cash = 100
else:
    cash = tuple(input("Your cash: \n").lower().split())[0]

# Set up modules
vision = Vision()
detector = Detector()

# Set some defaults for loops
board_cards = None
stages = ["Preflop", "Flop", "Turn", "River"]
suits = ["d", "h", "s", "c"]
ranks = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
actions = ["c", "f", "r"]

# Special positions
small = nr_of_players - 2
big = nr_of_players - 1

# Get position of dealer and order of turn
dealer_pos = detector.get_dealer(display=False)
players_sorted, my_turn = sort_players(players_pos, dealer_pos, nr_of_players)

# Create players and set bet for Preflop
players = []
for index, player_loc in enumerate(players_sorted):
    if index == small:
        players.append(Player(player_loc, ante / 2))
    elif index == big:
        players.append(Player(player_loc, 0))
    else:
        players.append(Player(player_loc, ante))

# Create action list and lock
actions = []
board = []
#actions_done = False
lock = threading.Lock()

t1 = threading.Thread(target=handle_actions)
t1.start()

# Loop through the stages of the game
for stage in stages:
    # While any player have his turn left
    while any([ind for ind in range(len(players)) if players[ind].inRound]):
        # Loop through all players
        for index, player in enumerate(players):
            if not player.inRound:
                continue

            # If it's my turn
            if index == my_turn+10:

                # wait for threading to be done
                lock.acquire()
                while actions:
                    lock.release()
                    time.sleep(2)
                    lock.acquire()
                lock.release()

                # Get my reaction                                                               -Handle my reaction
                reaction = (input("What you do?: \n"))
                if reaction == "f":
                    player.inGame = False
                    player.inRound = False
            else:
                #Get that player's action
                choice = detector.get_action(player.location, threshold=0.80)
                with lock:
                    actions.append((choice, player, index))
                player.inRound = False

        # If everyone is done but not all actions have been handled (a potential raise) then wait
        if not any([ind for ind in range(len(players)) if players[ind].inRound]):
            lock.acquire()
            while actions:
                lock.release()
                time.sleep(0.75)
                lock.acquire()
            lock.release()

    loc, cards = detector.get_board(False)
    print(cards)

    if stage == "Preflop":
        players = players[-2:] + players[:-2]
        my_turn = (my_turn + 2) % 6
