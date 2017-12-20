import cv2 as cv
from PIL import Image, ImageGrab
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter
import os

from tests import tests

MY_RESOLUTION = '1920x1080'
METHODS = ['cv.TM_CCOEFF', 'cv.TM_CCOEFF_NORMED', 'cv.TM_CCORR_NORMED', 'cv.TM_SQDIFF', 'cv.TM_SQDIFF_NORMED']

TEST_SIZE = (110, 110)
MAP_SIZE = (896, 896)

SUBREGION = {
    '1920x1080': (1615, 1895, 25, 305),
    '1680x1050': (1383, 1656, 24, 297),
}

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
        print('No Consensus')
        final_result = None
    else:
        final_result = results.most_common()[0][0]
        print('Consensus reached:', final_result)
    return final_result


def run(img, resolution, show_graphs=False, verbose=False):
    if resolution not in SUBREGION.keys():
        raise ValueError('Resolution not supported.')

    full_map = cv.imread('full_map.png', 0)
    test_sq = get_minimap(img, resolution)
    test_sq = cv.resize(test_sq, TEST_SIZE)

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

        if verbose:
            print(res_x, res_y, meth)
        results[(res_x, res_y)] += 1
        if meth == 'cv.TM_CCOEFF' and show_graphs:
            plot_result(img, template, top_left, bottom_right, meth)
           
    return determine_final_result(results)


    

# def make_a_map():
#     points = [
#         (491, 557),
#         (545, 485),
#         (520, 373),
#         (425, 401),
#         (499, 325),
#         (576, 307),
#     ]

#     your_map = cv.imread('full_map.png', 1)

#     for i, point in enumerate(points):
#         if point == points[-1]:
#             break
#         else:
#             next_point = points[i+1]
#         cv.line(your_map, point, next_point, (255,100,0), 2)

#     your_map = cv.cvtColor(your_map, cv.COLOR_BGR2RGB)
#     plt.imshow(your_map)
#     plt.show()



if __name__ == '__main__':
    for img_path, result, resolution in tests:
        print('Testing {}'.format(img_path))
        if not os.path.isfile(img_path):
            raise ValueError('Image designated by path "{}" does not exist.'.format(img_path))
        img = cv.imread(img_path, 0)
        if not result == 'skip':
            assert run(img, resolution) == result
            print('---PASS: [{}]---\n'.format(img_path))
        else:
            print(run(img, resolution, show_graphs=True))


# https://docs.opencv.org/trunk/d4/dc6/tutorial_py_template_matching.html