from Entities.Classes.Card import Card
import random


class Deck:

    def __init__(self):
        self.cards = [Card(suit, value) for suit in ["h", "d", "c", "s"]
                      for value in [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]]

    def shuffle(self):
        random.shuffle(self.cards)

    def manipulate(self, my_cards, board_cards, my_turn, nr_of_players):

        if my_cards is not None:
            for ind, my_card in enumerate(my_cards):
                for index, deck_card in enumerate(self.cards):
                    if deck_card.rank == my_card.rank and deck_card.suit == my_card.suit:
                        self.cards[index], self.cards[my_turn + nr_of_players * ind] = self.cards[
                            my_turn + nr_of_players * ind], self.cards[index]

        if board_cards is not None:
            for ind, board_card in enumerate(board_cards):
                for index, deck_card in enumerate(self.cards):
                    if deck_card.suit == board_card.suit and deck_card.rank == board_card.rank:
                        self.cards[index], self.cards[2 * nr_of_players + ind] = self.cards[2 * nr_of_players + ind], \
                        self.cards[index]

    def draw(self):
        if not self.is_empty():
            return self.cards.pop(0)
        else:
            return None

    def is_empty(self):
        return len(self.cards) == 0

    def __str__(self):
        return f"Deck of {len(self.cards)} cards"


