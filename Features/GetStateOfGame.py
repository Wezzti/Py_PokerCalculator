from Services.Vision import *
from configparser import ConfigParser

div_folder = 'C:/Users/Shadow/Documents/Repositories/PokerCalculator/Services/Python/Images/Cards/Div'
vision = Vision()

config = ConfigParser()
config.read('AppConfig.ini')

players_top_left = (int(config['players']['top_x']), int(config['players']['top_y']))
players_bottom_left = (int(config['players']['bottom_x']), int(config['players']['bottom_y']))


# Returns collection of (top_left_x, top_left_y, bottom_right_x, bottom_right_y) as well as cards
def get_board(threshold=0.82, display=False):
    top_left = (int(config['board']['top_x']), int(config['board']['top_y']))
    bottom_right = (int(config['board']['bottom_x']), int(config['board']['bottom_y']))
    # Remove here means that we don't remove the square that is made up of the given coordinates
    remove = False
    locations, cards = vision.find_cards(threshold, display=display, top_left=top_left,
                                         bottom_right=bottom_right, remove=remove)

    return cards





get_players(display=True)
#get_board(display=True)