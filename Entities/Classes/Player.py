class Player:

    def __init__(self, location, bet):
        self.hand = []
        self.scores = {
            "Score": 0,
            "Highest Rank": 0,
            "Highest Kicker": 0
        }
        self.inGame = True
        self.inRound = True
        self.hasPaid = False
        self.wins = 0
        self.cash = 1000
        self.location = location
        self.bet = bet

    def add_card(self, card):
        self.hand.append(card)

    def remove_card(self, card):
        self.hand.remove(card)

    def show_hand(self):
        print(f"{self.name}'s hand:")
        for card in self.hand:
            print(card)

    def reset(self):
        self.hand = []
        self.scores = {
            "Score": 0,
            "Highest Rank": 0,
            "Highest Kicker": 0
        }

    def pay(self):
        bet = self.bet
        self.cash -= bet
        self.bet -= bet
        return bet

    def set_ingame(self, x):
        self.inGame = x
        self.inRound = x

    def __str__(self):
        return self.name