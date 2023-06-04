import threading

from Entities.Classes.Card import Card
from Entities.Classes.Player import Player
from Features.Game import Game
from Features.GetLocations import *
from Features.Statics import *
import time


# Obsolete
# def getCard():
#     card = tuple(input("Give a card: suit and rank \n").lower().split())
#     while len(card) < 2 or suits.count(card[0]) == 0 or ranks.count(int(card[1])) == 0:
#         card = tuple(input("Try again: ").lower().split())
#     return Card(card[0], int(card[1]))
#
#
# def getAction(index, players):
#     action = tuple(input("What did player " + str(index) + " do: Check, fold or raise? \n").lower().split())[0]
#     while actions.count(action[0]) == 0:
#         action = tuple(input("Try again: c, f or r").lower().split())[0]
#     if action == 'r':
#         for player in players:
#             player.inRound = True
#
#     return action


# def getMyCards(debug):
#     my_cards = []
#
#     if debug:
#         my_cards.append(Card("hearts", 14))
#         my_cards.append(Card("diamonds", 14))
#     else:
#         for i in range(2):
#             my_cards.append(getCard())
#     return my_cards


def get_prob():
    my_prob = Game(players, my_cards, board_cards, my_turn, nr_of_players, runs)
    recalculate = False
    print("Your probability to win is: {} \n".format(my_prob))

    for player in players:
        player.wins = 0
    return recalculate


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
                    print("Player called")

                case "Fold":
                    pending.pop(0)
                    participant.set_ingame(False)
                    print("Player folded")

                case "Raise" | "Bet" | "AllIn":

                    # Branch this
                    raised = float(input("Player: " + str(index + 1) + " raised by? \n"))
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
#while True:
#    players_pos = localizer.get_players(display=True)
players_pos = [(928, 769, 1060, 801), (295, 581, 433, 613), (340, 264, 476, 296), (852, 168, 979, 197), (1444, 266, 1570, 297), (1486, 584, 1611, 614)]


nr_of_players = int(config["game"]["nr_players"])
dealer_pos = localizer.get_dealer(display=False)

# Sort players and get my position
players_sorted, my_turn = sort_players(players_pos, dealer_pos, nr_of_players)

# stages = ["Preflop", "Flop", "Turn", "River", "Showdown"]
# while True:
#     players_sorted, my_turn = sort_players(players_pos, dealer_pos, nr_of_players)
#
#     for stage in stages:
#         removes = []
#         for index, player_loc in enumerate(players_sorted):
#             action = localizer.get_action(player_loc)
#             print(action)
#             if action == "Fold":
#                 removes.append(index)
#         if stage == "Preflop":
#             players_sorted = players_sorted[-2:] + players_sorted[:-2]
#             for i in range(len(removes)):
#                 removes[i] = (removes[i] + 2) % nr_of_players
#         print("")
#         print("")
#         iterator = 0
#         for remove in removes:
#             players_sorted.pop(remove - iterator)
#             iterator += 1


# while True:
#     locations, cards = localizer.find_cards(top_left=board_top_left, bottom_right=board_bottom_right)
#     if locations is not None:
#         print(cards)


# Set some defaults for loops
board_cards = None
stages = ["Preflop", "Flop", "Turn", "River", "Showdown"]
suits = ["d", "h", "s", "c"]
ranks = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
actions = ["c", "f", "r"]

# Set my values
ante = int(config["game"]["ante"])
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
            if index == my_turn:
                lock.acquire()
                while actions:
                    lock.release()
                    time.sleep(2)
                    lock.acquire()
                lock.release()
                reaction = (input("What you do?: \n"))
                print(reaction)


            else:
                # Get that player's action
                choice = localizer.get_action(player.location)
                lock.acquire()
                actions.append((choice, player))
                lock.release()


            #match action:
            #    case "Call" | "Check":
#
            #        # This needs to wait for the raise branch to be done
            #        pot += player.pay()
            #        player.inRound = False
            #        # -----
            #        # Or does it?
#
            #    case "Fold":
            #        player.set_ingame(False)
#
            #    case "Raise" | "Bet" | "AllIn":
#
            #        # Branch this
            #        raised = int(input("Player: " + str(index + 1) + " raised by? \n"))
            #        for opponent in [opponent for opponent in players if opponent.inGame]:
            #            opponent.inRound = True
            #            opponent.bet += raised
#
            #        pot += player.pay()
            #        #----
#
            #        player.inRound = False
#
            #print(pot)

    if stage == "Preflop":
        players = players[-2:] + players[:-2]

    if stage == "Showdown":
        a = 1





## Initiate players
#players = []
#for i in range(nr_of_players):
#    players.append(Player(players_sorted[i]))
#
#players[my_turn].cash = cash
#
#pot = 0
#for index, player in enumerate(players):
#    # Big ante is always the person last to decide. The -1 is because we start counting at 0.
#    if index == nr_of_players - 1:
#        pot += player.pay(ante)
#        player.hasPaid = True
#
#    # Small ante is always second to last to decide.
#    elif index == nr_of_players - 2:
#        pot += player.pay(ante / 2)
#        # HAS NOT PAID FULL. IS ALLOWED TO CHECK CARDS BUT NOT THE FLOP UNTIL REST OF ANTE IS PAID                                          !!!!!!!!
#        player.hasPaid = True
#
#for stage in stages:
#    print("Stage: {}".format(stage))
#
#    # We set that everyone is inRound, but what if they have folded?
#    for player in players:
#        player.inRound = True
#
#    rounds = 0
#    reCalculate = True
#    while [player.inRound for player in players].count(True) != 0:
#        for index, player in enumerate(players):
#
#            if index == my_turn:
#                if stage == "Preflop" and rounds == 0:
#                    my_cards = getMyCards(debug)
#
#                if reCalculate:
#                    reCalculate = get_prob()
#
#                action = getAction("I", players)
#
#                player.inRound = False
#
#
#
#
#
#
#            elif player.inGame:
#                action = getAction(index + 1, players)
#                if action == "f":
#                    player.inGame = False
#                    reCalculate = True
#
#                player.inRound = False
#
#        rounds = 1
#