import threading

from Entities.Classes.Card import Card
from Entities.Classes.Player import Player
from Features.Game import Game
from Features.GetLocations import *
from Features.Statics import *
import time


def handle_actions():
    lock.acquire()
    done = actions_done
    pending = actions
    lock.release()
    money = 1.5 * ante

    while not (not pending and done):
        if pending:
            action, participant = pending[0]

            match action:
                case "Call" | "Check":

                    # This needs to wait for the raise branch to be done
                    pending.pop(0)
                    money += player.pay()
                    participant.inRound = False
                    # -----
                    # Or does it?
                    print("Player: " + str(index) + " called")

                case "Fold":
                    pending.pop(0)
                    participant.set_ingame(False)
                    print("Player: " + str(index) + " folded")

                case "Raise" | "Bet" | "AllIn":

                    # Branch this
                    print("Player: " + str(index) + " raised")
                    #raised = float(input("Player: " + str(index) + " raised by? \n"))
                    raised = 1
                    pending.pop(0)
                    for opponent in [opponent for opponent in players if opponent.inGame]:
                        opponent.inRound = True
                        opponent.bet += raised

                    money += participant.pay()
                    # ----

                    participant.inRound = False
        else:
            time.sleep(1)
            lock.acquire()
            pending = actions
            done = actions_done
            lock.release()


# Program settings
debug = True

# Config
config = ConfigParser()
config.read('AppConfig.ini')

# Simulation settings
runs = int(config["game"]["runs"])

# Set up modules
vision = Vision()
localizer = Localizer()

# Get player positions

# players_pos = localizer.get_players(display=True)
players_pos = [
    (928, 769, 1060, 801),
    (295, 581, 433, 613),
    (340, 264, 476, 296),
    (852, 168, 979, 197),
    (1444, 266, 1570, 297),
    (1486, 584, 1611, 614)
]

nr_of_players = int(config["game"]["nr_players"])
dealer_pos = localizer.get_dealer(display=False)

# Sort players and get my position
players_sorted, my_turn = sort_players(players_pos, dealer_pos, nr_of_players)


# Set some defaults for loops
board_cards = None
stages = ["Preflop", "Flop", "Turn", "River", "Showdown"]
suits = ["d", "h", "s", "c"]
ranks = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
actions = ["c", "f", "r"]

# Set my values
ante = float(config["game"]["ante"])
nr_of_players = int(config["game"]["nr_players"])
if debug:
    cash = 100
else:
    cash = tuple(input("Your cash: \n").lower().split())[0]

# Special positions
small = nr_of_players - 2
big = nr_of_players - 1

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
actions_done = False
lock = threading.Lock()

# Create pot. Begins at sum of small and big ante.

t1 = threading.Thread(target=handle_actions)
t1.start()
# Loop through the stages of the game
for stage in stages:
    # While any player have his turn left
    while any([ind for ind in range(len(players)) if players[ind].inRound]):
        # Loop through all players
        for index, player in enumerate(players):
            # If player already has folded, continue to next player
            if not player.inRound:
                continue

            # If it's my turn, wait for threading to be done and then...
            if index == my_turn+10:
                lock.acquire()
                while actions:
                    lock.release()
                    time.sleep(2)
                    lock.acquire()
                lock.release()
                reaction = (input("What you do?: \n"))
                if reaction == "f":
                    player.inGame = False
                    player.inRound = False

            else:
                # Get that player's action
                choice = localizer.get_action(player.location, threshold=0.85)
                lock.acquire()
                actions.append((choice, player))
                lock.release()

    if stage == "Preflop":
        players = players[-2:] + players[:-2]

    if stage == "Showdown":
        a = 1

    time.sleep(2)