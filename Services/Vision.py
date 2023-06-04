import numpy as np
import win32gui, win32ui, win32con
from time import time
import cv2 as cv
import os
from threading import Lock
from imutils.object_detection import non_max_suppression


class Vision:
    # Properties
    # haystack_img = None
    # displayed_ranks = np.array([1337])
    # iterator = 0
    # rank_dir = 'C:/Users/Shadow/Documents/Repositories/PokerCalculator/Services/Python/Images/Cards/Rank'
    # suit_dir = 'C:/Users/Shadow/Documents/Repositories/PokerCalculator/Services/Python/Images/Cards/Suit'

    def __init__(self, monitor_width=1920, monitor_height=1080, focused_window=None, FPS=False,
                 alpha=True, ascontiguous=True):
        self.monitor_width = monitor_width
        self.monitor_height = monitor_height
        self.focused_window = focused_window
        self.FPS = FPS
        self.alpha = alpha
        self.ascontiguous = ascontiguous
        self.lock = Lock()

    def window_capture(self):
        if self.focused_window is None:
            hwnd = None
        else:
            hwnd = win32gui.FindWindow(None, self.focused_window)

        wDC = win32gui.GetWindowDC(hwnd)
        dcObj = win32ui.CreateDCFromHandle(wDC)
        cDC = dcObj.CreateCompatibleDC()
        dataBitMap = win32ui.CreateBitmap()
        dataBitMap.CreateCompatibleBitmap(dcObj, self.monitor_width, self.monitor_height)
        cDC.SelectObject(dataBitMap)
        cDC.BitBlt((0, 0), (self.monitor_width, self.monitor_height), dcObj, (0, 0), win32con.SRCCOPY)

        # save the screenshot
        # dataBitMap.SaveBitmapFile(cDC, 'debug.bmp')

        signedIntsArray = dataBitMap.GetBitmapBits(True)
        img = np.fromstring(signedIntsArray, dtype='uint8')
        if img is None:
            raise Exception("Couldn't find your screen")

        img.shape = (self.monitor_height, self.monitor_width, 4)

        # Free Resources
        dcObj.DeleteDC()
        cDC.DeleteDC()
        win32gui.ReleaseDC(hwnd, wDC)
        win32gui.DeleteObject(dataBitMap.GetHandle())

        # drop the alpha channel, or cv.matchTemplate() will thow an error like:
        #   error: (-215:Assertion failed) (depth == CV:BU ...)
        if self.alpha:
            img = img[..., :3]

        # make image C_CONTIGIOUS to avoid errors that look like:
        #   File ... in draw_rectangles ...
        if self.ascontiguous:
            img = np.ascontiguousarray(img)

        return img

    @staticmethod
    def snip_screen(img, top_left, bottom_right, exclude=False):
        if exclude:
            img[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0], :] = 0
            return img
        else:
            return img[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]

    def display(self, locations, line_color=(0, 255, 0), line_type=cv.LINE_4, thickness=2):
        # This function displays whatever locations are given to it.
        # The form of locations need be list of tuples, as such: [(0,0,1920,1080), (w1, h1, w2, h2)]

        haystack_img = self.window_capture()
        for location in locations:
            loc_array = location.flatten()
            cv.rectangle(haystack_img, (loc_array[0], loc_array[1]), (loc_array[2], loc_array[3]), color=line_color,
                         thickness=thickness, lineType=line_type)

        cv.imshow('Result', haystack_img)
        if cv.waitKey(20) & 0xFF == ord('q'):
            cv.destroyAllWindows()

    def match(self, img, image_path, threshold, top_left=(0, 0), bottom_right=(1920, 1080), exclude=False,
              method=cv.TM_CCOEFF_NORMED, display=False):
        # This function tries to find and return the location on screen of any image-path that is given.
        # Not restricted to cards per se

        haystack_img = Vision.snip_screen(img, top_left, bottom_right, exclude)
        #haystack_img = self.snip_screen(img, top_left, bottom_right, exclude)
        # Convert and interpret image
        needle_img = cv.imread(image_path, method)
        if needle_img is None:
            raise Exception("Cannot find needle image")
        needle_h, needle_w = needle_img.shape[0], needle_img.shape[1]

        # Find needle in haystack using given method
        result = cv.matchTemplate(haystack_img, needle_img, method)
        # Get location of significant matches:
        #   locations is a list of tuple:4 containing coordinate of top left and bottom right
        locations = np.where(result >= threshold)
        locations = list(zip(*locations[::-1]))
        if len(locations) == 0:
            return None

        # Add bottom right location to the top left location tuple
        if exclude:
            locations = [(x[0],
                          x[1],
                          x[0] + needle_w,
                          x[1] + needle_h) for x in locations]
        else:
            locations = [(x[0] + top_left[0],
                          x[1] + top_left[1],
                          x[0] + top_left[0] + needle_w,
                          x[1] + top_left[1] + needle_h) for x in locations]

        # Merge similar matches
        locations = non_max_suppression(np.array(locations))

        if display:
            self.display(locations)

        return locations

#    def get_suits(self, locations, method=cv.TM_CCOEFF_NORMED):
#        # Function takes the location of cards, check beneath them for their suit and return result if
#        # suits for all cards were found.
#        if locations is None:
#            return None
#        suits = []
#        # If any cards to get the suit to
#        if len(locations) > 0:
#            # Loop through all cards whose suits are requested
#            suit_dir = 'C:/Users/Shadow/Documents/Repositories/PokerCalculator/Services/Python/Images/Cards/Suit'
#            for location in locations:
#                # Check only beneath the card in question
#                sub_image = self.haystack_img[:, location[0] - min(30, location[0]):location[2] + 30, :]
#
#                # Loop through every possible suit
#                for suit in os.listdir(suit_dir):
#                    needle_img = cv.imread(self.suit_dir+'/{}'.format(suit), method)
#
#                    # If suit is found underneath card..
#                    result = cv.matchTemplate(sub_image, needle_img, method)
#                    min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
#                    if max_val < 0.90:
#                        continue
#                    else:
#                        # .. save that suit
#                        suits.append(suit[0])
#
#        # If any card didn't get its suit, return None
#        if len(suits) != len(locations):
#            print("Couldn't find match for one or more cards")
#            return None
#
#        return suits

#    def find_cards(self, threshold, display=False, top_left=(0, 0), bottom_right=(1920, 1080), remove=False):
#        # Function check for cards, shown as saved in Rank folder.
#        # Optimal parameter to limited search area.
#
#        # Loop ends on return. Return happens only at board-stage-change
#        while True:
#            # Loop through all ranks
#            ranks = np.array([])
#            cards = []
#            locations = []
#            for image in os.listdir(self.rank_dir):
#                # If there's a match on the current rank, save the rank location the suit.
#                # Note that there can be several matches per rank
#                # Also, location is saved in order to display if so desired
#                rank_locs = self.match(self.rank_dir + '/{}'.format(image), threshold, top_left=top_left,
#                                       bottom_right=bottom_right, remove=remove)
#
#                suits = self.get_suits(rank_locs)
#
#                # If no match on this rank, go to next one
#                if rank_locs is None or suits is None:
#                    continue
#
#                # Save the location of the rank
#                if len(rank_locs) > 1:
#                    for rank_loc in rank_locs:
#                        locations.append(rank_loc)
#                else:
#                    locations.append(rank_locs)
#
#                for i in range(len(rank_locs)):
#                    # For each occurrence of the rank, save it along with its corresponding suit
#                    cards.append((int(image.replace(".jpg", "")), suits[i]))
#                    ranks = np.append(ranks, int(image.replace(".jpg", "")))
#
#            # If we found any match, the match differ from previous match and the amount of cards make sense, return
#            # Take note that the game can start at any amount of cards >= 3. (For the sake of debug)
#            if len(locations) != 0 and not np.array_equal(ranks, self.displayed_ranks) \
#                    and (len(ranks) > len(self.displayed_ranks)
#                         or (len(ranks) == 3 and (len(self.displayed_ranks == 5) or len(self.displayed_ranks == 1)))) \
#                    and len(ranks) >= 3:
#
#                # Needs to have happened twice. This is so that the board doesn't get
#                # updated whilst cards are being removed from the board
#                if self.iterator < 1:
#                    self.iterator += 1
#                else:
#                    if display and locations is not None:
#                        arrays = [location.flatten() + [top_left[0], top_left[1], top_left[0],
#                                                        top_left[1]] for location in locations]
#                        self.display(arrays)
#
#                    self.displayed_ranks = ranks
#                    self.iterator = 0
#                    return locations, cards
#