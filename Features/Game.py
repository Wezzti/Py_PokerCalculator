from Entities.Classes.Deck import Deck
from Entities.Classes.Board import Board
from Features.Find_winner import find_winner

# This module takes the players, my cards, the card on board, the number of players as well as numbers of runs to be
# performed and returns my win_rate


def Game(players, my_cards, board_cards, my_turn, nr_of_players, runs):
    for i in range(runs):

        # Reset players
        for player in players:
            player.reset()

        # Initialize deck
        deck = Deck()
        deck.shuffle()
        deck.manipulate(my_cards, board_cards, my_turn, nr_of_players)

        # Initialize board
        board = Board()

        # Blinds
        for i in range(2):
            for player in players:
                player.add_card(deck.draw())

        # Preflop
        for i in range(3):
            board.add_card(deck.draw())

        # Flop
        board.add_card(deck.draw())

        # River
        board.add_card(deck.draw())

        find_winner(players, board)

    # Get probability of me winning
    for index, player in enumerate(players):
        if index == my_turn:
            return player.wins / runs














