from ast import Lambda
from queue import Empty
from py_linq import Enumerable

# This module takes players and the board and sets the score attributes of each player


def find_winner(players, board):
    scores = {
        "royal flush": 10,
        "straight flush": 9,
        "flush": 6,
        "straight": 5,
        "four of a kind": 8,
        "full house": 7,
        "three of a kind": 4,
        "two pair": 3,
        "pair": 2,
        "high card": 1,
    }

    # Returns <score>, <Highest Rank>, <Highest kicker rank>
    def get_scores(hand, board):
        cards = hand + board
        sorted_hand = sorted(cards, key=lambda card: card.rank)

        # Checks for royal flush, straight flush, flush and straight

        for i in range(3):
            # If straight
            if sorted_hand[i].rank == sorted_hand[i + 1].rank + 1 == sorted_hand[i + 2].rank + 2 == sorted_hand[
                i + 3].rank + 3 == sorted_hand[i + 4].rank + 4:
                # If flush
                if sorted_hand[i].suit == sorted_hand[i + 1].suit == sorted_hand[i + 2].suit == sorted_hand[
                    i + 3].suit == sorted_hand[i + 4].suit:
                    # If royal
                    if sorted_hand[i].rank == 14:
                        return scores["royal flush"], sorted_hand[i].rank, None
                    else:
                        return scores["straight flush"], sorted_hand[i].rank, None

                else:
                    return scores["straight"], sorted_hand[i].rank, None
            elif sorted_hand[i].suit == sorted_hand[i + 1].suit == sorted_hand[i + 2].suit == sorted_hand[i + 3].suit == \
                    sorted_hand[i + 4].suit:
                return scores["flush"], sorted_hand[i].rank, None

        # Check for other hands
        ranks = [card.rank for card in sorted_hand]
        ranks_set = set([card.rank for card in sorted_hand])

        # Check for four-of-a-kind
        if len(Enumerable(ranks_set).where(lambda x: ranks.count(x) == 4)) != 0:
            rank = Enumerable(ranks_set).where(lambda x: ranks.count(x) == 4)[0]
            return scores["four of a kind"], rank, max([card.rank for card in sorted_hand if card.rank != rank])

        # Check for full-house
        elif len(Enumerable(ranks_set).where(lambda x: ranks.count(x) == 3)) != 0 and len(
                Enumerable(ranks_set).where(lambda x: ranks.count(x) == 2)) != 0:
            rank = Enumerable(ranks_set).where(lambda x: ranks.count(x) == 3)[0]
            return scores["full house"], rank, None

        # Check for three-of-a-kind
        elif len(Enumerable(ranks_set).where(lambda x: ranks.count(x) == 3)) != 0:
            rank = Enumerable(ranks_set).where(lambda x: ranks.count(x) == 3)[0]
            return scores["three of a kind"], rank, max([card.rank for card in sorted_hand if card.rank != rank])

        # Check for two-pair
        elif len(Enumerable(ranks_set).where(lambda x: ranks.count(x) == 2)) > 1:

            rank = Enumerable(ranks_set).where(lambda x: ranks.count(x) == 2)
            # Get the two highest pairs
            sorted_rank = sorted(rank, reverse=True)

            return scores["two pair"], sorted_rank[0], max(
                [card.rank for card in sorted_hand if card.rank != sorted_rank[0] and card.rank != sorted_rank[1]])

        # Check for pair
        elif len(Enumerable(ranks_set).where(lambda x: ranks.count(x) == 2)) != 0:
            rank = Enumerable(ranks_set).where(lambda x: ranks.count(x) == 2)[0]
            return scores["pair"], rank, max([card.rank for card in sorted_hand if card.rank != rank])

        # Else highest card
        else:
            rank = max([card.rank for card in sorted_hand if hand.count(card) == 1])
            return scores["high card"], rank, max([card.rank for card in sorted_hand if card.rank != rank])

    # Get everyones ratings
    for player in players:
        if player.inGame:
            score, rank, kicker = get_scores(player.hand, board.cards)
            player.scores["Score"] = score
            player.scores["Highest Rank"] = rank
            player.scores["Highest Kicker"] = kicker

    # Decide the winner
    players = [player for player in players if player.inGame]
    highest_score = Enumerable(players).max(lambda x: x.scores["Score"])
    highest_score_players = [player for player in players if player.scores["Score"] == highest_score]
    if len(highest_score_players) == 1:
        highest_score_players[0].wins += 1

    else:
        highest_card = Enumerable(highest_score_players).max(lambda x: x.scores["Highest Rank"])
        highest_card_players = [player for player in highest_score_players if
                                player.scores["Highest Rank"] == highest_card]
        if len(highest_card_players) == 1:
            highest_card_players[0].wins += 1

        elif [10, 9, 6, 5, 7].count(highest_score) == 0:
            highest_kicker = Enumerable(highest_card_players).max(lambda x: x.scores["Highest Kicker"])
            highest_kicker_players = [player for player in highest_card_players if
                                      player.scores["Highest Kicker"] == highest_kicker]
            if len(highest_kicker_players) < 2:
                highest_kicker_players[0].wins += 1
