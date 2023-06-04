from Entities.Classes.Card import *
from Entities.Classes.Player import *
from Entities.Classes.Deck import *
from Entities.Classes.Board import *

from Features.Game import *
from configparser import ConfigParser

# Set parameters
config = ConfigParser()
config.read('AppConfig.ini')

board_top_left = (int(config['board']['top_x']), int(config['board']['top_y']))
board_bottom_left = (int(config['board']['bottom_x']), int(config['board']['bottom_y']))
players_top_left = (int(config['players']['top_x']), int(config['players']['top_y']))
players_bottom_left = (int(config['players']['bottom_x']), int(config['players']['bottom_y']))
nr_of_players = int(config["game"]["nr_players"])
runs = int(config["game"]["runs"])
ante = int(config["game"]["ante"])


suits = ["d", "h", "s", "c"]
ranks = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
actions = ["c", "f", "r"]



def getCard():
    card = tuple(input("Give a card: suit and rank \n").lower().split())
    while len(card) < 2 or suits.count(card[0]) == 0 or ranks.count(int(card[1])) == 0:
        card = tuple(input("Try again: ").lower().split())
    return Card(card[0], int(card[1]))


def getAction(index, players):
    action = tuple(input("What did player " + str(index) + " do: Check, fold or raise? \n").lower().split())[0]
    while actions.count(action[0]) == 0:
        action = tuple(input("Try again: c, f or r").lower().split())[0]
    if action == 'r':
        for player in players:
            player.inRound = True

    return action


def getMyCards(debug):
    my_cards = []

    if debug:
        my_cards.append(Card("hearts", 14))
        my_cards.append(Card("diamonds", 14))
    else:
        for i in range(2):
            my_cards.append(getCard())
    return my_cards


def get_prob():
    my_prob = Game(players, my_cards, board_cards, my_turn, nr_of_players, runs)
    reCalculate = False
    print("Your probability to win is: {} \n".format(my_prob))

    for player in players:
        player.wins = 0
    return reCalculate