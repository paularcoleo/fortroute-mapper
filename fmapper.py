'''Fortroute Mapper takes screenshots of Fortnite BR minimap to map out a route through a match.'''

import cv2
import numpy as np
import os, sys, time
from PIL import ImageGrab
from collections import Counter

from settings import LOCATION_FOLDER, MY_RESOLUTION

TEST_SIZE = (133, 133)
MAP_SIZE = (1010, 1010)
SUBREGION = {
    '1920x1080': (1615, 25, 1895, 305),
    '1680x1050': (24, 1383, 297, 1656),
}
MAP_FILE = './fortnite_map.png'
MAP_GRAY = cv2.imread(MAP_FILE, 0)
MAP_COLOR = cv2.imread(MAP_FILE, 1)
METHODS = ['cv2.TM_CCOEFF', 'cv2.TM_CCOEFF_NORMED', 
           'cv2.TM_CCORR_NORMED', 'cv2.TM_SQDIFF', 'cv2.TM_SQDIFF_NORMED']
LINE_COLOR_BGR = (0,100,255)

def grab_minimap():
    im = ImageGrab.grab(bbox=SUBREGION[MY_RESOLUTION])
    im2 = np.array(im, dtype='uint8')
    im3 = cv2.cvtColor(im2, cv2.COLOR_BGR2GRAY)
    return im3

def process_minimap(minimap):
    img = cv2.resize(minimap, TEST_SIZE)
    votes = Counter()
    for m in METHODS:
        template = MAP_GRAY.copy()
        method = eval(m)

        res = cv2.matchTemplate(img, template, method)
        _, _, min_loc, max_loc = cv2.minMaxLoc(res)

        top_left = min_loc if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED] else max_loc
        res_x, res_y = int(top_left[0] + TEST_SIZE[0]/2), int(top_left[1] + TEST_SIZE[1]/2)

        votes[(res_x, res_y)] += 1
    return votes

def determine_result(votes):
    return None if len(votes) > 2 else votes.most_common()[0][0]

def reset_current_map():
    game_map = cv2.imread(MAP_FILE, 1)
    default = 'current_map.png'
    cv2.imwrite(os.path.join(LOCATION_FOLDER, default), game_map)
    print('Map file reset.')

def update_map(points):
    clr_map = MAP_COLOR.copy()
    for i, point in enumerate(points):
        if point == points[-1]:
            cv2.circle(clr_map, point, 10, LINE_COLOR_BGR, -1)
            break
        else:
            next_point = points[i+1]
        cv2.line(clr_map, point, next_point, LINE_COLOR_BGR, 3)
    cv2.imwrite(os.path.join(LOCATION_FOLDER, 'current_map.png'), clr_map)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == 'start':
            reset_current_map()
            points = []
            i = 1
            while(i):
                minimap = grab_minimap()
                coord = determine_result(process_minimap(minimap))
                print(i, coord, len(points))
                if coord:
                    points.append(coord)
                update_map(points)
                sleep_time = 10 if i > 30 else 5
                time.sleep(sleep_time)
                i += 1

        elif sys.argv[1] == 'reset':
            reset_current_map()
    else:
        print('Please specify something... idiot.')