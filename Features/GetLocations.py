import numpy as np

from Services.Vision import *
import cv2 as cv
from configparser import ConfigParser


class Localizer:
    # Config
    config = ConfigParser()
    config.read('AppConfig.ini')
    vision = Vision()
    iterator = 0
    displayed_ranks = np.array([1337, 50052])
    div_folder = config["paths"]["div"]

    def get_board(self, display=False):
        # Function check for cards, shown as saved in Rank folder.
        # Optimal parameter to limited search area.

        top_left = (int(self.config['board']['top_x']), int(self.config['board']['top_y']))
        bottom_right = (int(self.config['board']['bottom_x']), int(self.config['board']['bottom_y']))

        rank_dir = self.config['paths']['rank']
        # Loop ends on return. Return happens only at board-stage-change
        while True:
            # Loop through all ranks
            ranks = np.array([])
            cards = []
            locations = []

            for image in os.listdir(rank_dir):
                # If there's a match on the current rank, save the rank location the suit.
                # Note that there can be several matches per rank
                # Also, location is saved in order to display if so desired
                img = self.vision.window_capture()

                rank_locs = self.vision.match(img, rank_dir + '/{}'.format(image), 0.82, top_left=top_left,
                                              bottom_right=bottom_right, exclude=False)

                suits = self.get_suits(img, rank_locs)

                # If no match on this rank, go to next one
                if rank_locs is None or suits is None:
                    continue

                # Save the location of the rank
                locations.extend(rank_locs)

                for i in range(len(rank_locs)):
                    # For each occurrence of the rank, save it along with its corresponding suit
                    cards.append((int(image.replace(".jpg", "")), suits[i]))
                    ranks = np.append(ranks, int(image.replace(".jpg", "")))

            if (locations is not None and
                    (len(locations) == len(self.displayed_ranks) + 1 or
                     (len(locations) == 3 and len(self.displayed_ranks) == 5))):

                # Needs to have happened twice. This is so that the board doesn't get
                # updated whilst cards are being removed from the board (5 => 3 gets broken)
                if self.iterator < 1:
                    self.iterator += 1
                else:
                    if display:
                        self.vision.display(locations)

                    self.displayed_ranks = ranks
                    self.iterator = 0
                    return locations, cards

    def get_suits(self, haystack_img, locations, method=cv.TM_CCOEFF_NORMED):
        # Function takes the location of cards, check beneath them for their suit and return result if
        # suits for all cards were found.
        while True:
            if locations is None:
                return None

            suits = []
            # If any cards to get the suit to
            if len(locations) > 0:
                # Loop through all cards whose suits are requested
                suit_dir = self.config['paths']['suit']
                for location in locations:
                    # Check only beneath the card in question
                    # Note that haystack_img is of shape (1080, 1920, 3) so y-axis first
                    marginal = 50
                    beneath_rank_img = haystack_img[(location[3] - marginal):,
                                       (location[0] - marginal):(location[2] + marginal), :]

                    # Loop through every possible suit
                    for suit in os.listdir(suit_dir):
                        needle_img = cv.imread(suit_dir + '/{}'.format(suit), method)

                        # If suit is found underneath card..
                        result = cv.matchTemplate(beneath_rank_img, needle_img, method)
                        min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
                        if max_val < 0.90:
                            continue
                        else:
                            # .. save that suit
                            suits.append(suit[0])
                            break

            # If any card didn't get its suit, return None
            if len(suits) == len(locations):
                return suits

    def get_action(self, location, method=cv.TM_CCOEFF_NORMED):
        while True:
            img = self.vision.window_capture()
            above_money = self.vision.snip_screen(img, (location[0], location[1] - 60), (location[2], location[3] - 30))
            action_dir = self.config['paths']['action']
            for action in os.listdir(action_dir):
                needle_img = cv.imread(action_dir + '/{}'.format(action), method)

                result = cv.matchTemplate(above_money, needle_img, method)
                min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
                if max_val < 0.72:
                    continue
                else:
                    return action.replace(".jpg", "")

    # Returns collection of (top_left_x, top_left_y, bottom_right_x, bottom_right_y)
    def get_players(self, display=False, threshold=0.37):
        #top_left = (int(config['players']['top_x']), int(config['players']['top_y']))
        #bottom_right = (int(config['players']['bottom_x']), int(config['players']['bottom_y']))
        ## Remove here means that we remove the square that is made up of the given coordinates
        #remove = True
#
        #locations = vision.match(div_folder + '/{}'.format("PlayerRef.jpg"),
        #                         threshold, top_left, bottom_right, remove, display=display)
#
        #return locations
        players_pos = None
        nr_of_players = int(self.config["game"]["nr_players"])
        players_top_left = (int(self.config['players']['top_x']), int(self.config['players']['top_y']))
        players_bottom_left = (int(self.config['players']['bottom_x']), int(self.config['players']['bottom_y']))
        img = self.vision.window_capture()
        while players_pos is None or len(players_pos) != nr_of_players:
            img = self.vision.window_capture()
            players_pos = self.vision.match(img, self.div_folder + '/PlayerRef.jpg', threshold, players_top_left,
                                            players_bottom_left, True, display=display)
        return players_pos

    def get_dealer(self, display=False):
        dealer_pos = None
        img = self.vision.window_capture()
        while dealer_pos is None:
            img = self.vision.window_capture()
            dealer_pos = self.vision.match(img, self.div_folder + '/Dealer.jpg', 0.85, display=display)
            if dealer_pos is not None:
                dealer_pos = dealer_pos.flatten()
        return dealer_pos
