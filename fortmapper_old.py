import cv2 as cv
from PIL import Image, ImageGrab
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter
import os, sys, time
from datetime import datetime


from settings import LOCATION_FOLDER
from tests import tests


MY_RESOLUTION = '1920x1080'
METHODS = ['cv.TM_CCOEFF', 'cv.TM_CCOEFF_NORMED', 'cv.TM_CCORR_NORMED', 'cv.TM_SQDIFF', 'cv.TM_SQDIFF_NORMED']

TEST_SIZE = (133, 133)
MAP_SIZE = (1010, 1010)

SUBREGION = {
    '1920x1080': (1615, 25, 1895, 305),
    '1680x1050': (24, 1383, 297, 1656),
}

MAP_FILE = './fortnite_map.png'

def get_minimap(img, resolution):
    x1, x2, y1, y2 = SUBREGION[resolution]
    return img[y1:y2, x1:x2]

def plot_result(img, template, tl, br, method):
    cv.rectangle(template, tl, br, 255, 5)
    plt.subplot(121)
    plt.imshow(img, cmap='gray')
    plt.title('Input Image'), plt.xticks([]), plt.yticks([])
    plt.subplot(122)
    plt.imshow(template, cmap='gray')
    plt.title('Detected Point'), plt.xticks([]), plt.yticks([])
    plt.suptitle(method)
    plt.show()

def determine_final_result(results):
    if len(results) > 2:
        # print('No Consensus')
        final_result = None
    else:
        final_result = results.most_common()[0][0]
        # print('Consensus reached:', final_result)
    return final_result


def run(img, resolution, show_graphs=False, verbose=False):
    if resolution not in SUBREGION.keys():
        raise ValueError('Resolution not supported.')

    full_map = cv.imread(MAP_FILE, 0)
    test_sq = cv.resize(img, TEST_SIZE)

    results = Counter()
    for meth in METHODS:
        template = full_map.copy()
        img = test_sq.copy()

        method = eval(meth)

        res = cv.matchTemplate(img, template, method)
        _, _, min_loc, max_loc = cv.minMaxLoc(res)

        top_left = min_loc if method in [cv.TM_SQDIFF, cv.TM_SQDIFF_NORMED] else max_loc
        bottom_right = (top_left[0] + TEST_SIZE[0], top_left[1] + TEST_SIZE[1])

        res_x, res_y = int(top_left[0] + TEST_SIZE[0]/2), int(top_left[1] + TEST_SIZE[1]/2)

        results[(res_x, res_y)] += 1
        if method == cv.TM_CCOEFF and show_graphs:
            plot_result(img, template, top_left, bottom_right, meth)

    if verbose:
        print(results)
    return determine_final_result(results)
  

def make_a_map(points, filename=None):
    your_map = cv.imread(MAP_FILE, 1)

    for i, point in enumerate(points):
        # if i == 0:
        #     continue
        if point == points[-1]:
            cv.circle(your_map, point, 10, (0,100,255), -1)
            break
        else:
            next_point = points[i+1]
        cv.line(your_map, point, next_point, (0,100,255), 3)

    # your_map = cv.cvtColor(your_map, cv.COLOR_BGR2RGB)
    if filename:
        cv.imwrite(filename, your_map)
    else:
        cv.imwrite('./tmp/map-{}.png'.format(datetime.strftime(datetime.now(), '%M-%d-%d')), your_map)


def reset_current_map():
    game_map = cv.imread(MAP_FILE, 1)
    default = 'current_map.png'
    cv.imwrite(os.path.join(LOCATION_FOLDER, default), game_map)
    print('Map file reset.')


if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == 'test':
            for img_path, result, resolution in tests:

                print('Testing {}'.format(img_path))
                if not os.path.isfile(img_path):
                    raise ValueError('Image designated by path "{}" does not exist.'.format(img_path))

                img = cv.imread(img_path, 0)
                
                if not result == 'skip':
                    # img = get_minimap(img, resolution)
                    assert run(img, resolution, verbose=True, show_graphs=True) == result
                    print('---PASS: [{}]---\n'.format(img_path))
                else:
                    print(run(img, resolution, show_graphs=True))
        
        elif sys.argv[1] == 'capture':
            i = 1
            while(i):
                im = ImageGrab.grab()
                im2 = np.array(im) 
                # Convert RGB to BGR 
                im2 = im2[:, :, ::-1].copy() 
                mmap = get_minimap(im2, MY_RESOLUTION)
                cv.imwrite('./tmp/test_{}.png'.format(i), mmap)
                print('.', end='', flush=True)
                time.sleep(10)
                i += 1


        elif sys.argv[1] == 'analyze':
            results = []
            i = 1
            while(os.path.isfile('./tmp/test_{}.png'.format(i))):
                print('.', end='', flush=True)
                img = cv.imread('./tmp/test_{}.png'.format(i), 0)
                # print(i)
                result = run(img, MY_RESOLUTION, verbose=False, show_graphs=False)
                # print('')
                if result:
                    results.append(result)
                i += 1
            if results:
                make_a_map(results)

        elif sys.argv[1] == 'start':
            reset_current_map()
            points = []
            i = 1
            while(i):
                im = ImageGrab.grab(bbox=SUBREGION[MY_RESOLUTION])
                im2 = np.array(im, dtype='uint8')
                # Convert BGR to GRAY for Template Matching
                test = cv.cvtColor(im2, cv.COLOR_BGR2GRAY)
                # break
                coord = run(test, MY_RESOLUTION)
                print(i, coord, len(points))
                if coord:
                    points.append(coord)
                make_a_map(points, filename=os.path.join(LOCATION_FOLDER, 'current_map.png'))
                time.sleep(10)
                i += 1

        elif sys.argv[1] == 'reset':
            reset_current_map()

        else:
            filename = sys.argv[1]
            img = cv.imread(filename, 0)
            # img = get_minimap(img, resolution=MY_RESOLUTION)
            output = run(img, MY_RESOLUTION, verbose=True, show_graphs=True)
            print(output)
    else:
        print('Specify a thing, dummy')


# https://docs.opencv.org/trunk/d4/dc6/tutorial_py_template_matching.html