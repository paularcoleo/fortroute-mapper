import cv2 as cv
from PIL import Image, ImageGrab
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter

MY_RESOLUTION = '1920x1080'

TEST_SIZE = (110, 110)
MAP_SIZE = (896, 896)

SUBREGION = {
    '1920x1080': (1615, 1895, 25, 305),
    '1680x1050': (1383, 1656, 24, 297),
}

TESTS = [
    ('test_images/test_01_full.jpg', (206, 557), '1920x1080'),
    ('test_images/test_02_full.jpg', (491, 557), '1920x1080'),
    ('test_images/test_03_full.jpg', (545, 485), '1920x1080'),
    ('test_images/test_04_full.jpg', (521, 373), '1920x1080'),
    ('test_images/test_05_full.jpg', (425, 401), '1920x1080'),
    ('test_images/test_06_full.jpg', (499, 325), '1920x1080'),
    ('test_images/test_07_full.jpg', (576, 307), '1920x1080'),
    ('test_images/test_07_full.jpg', (576, 307), '1920x1080'),
    ('test_images/bad_01_full.jpg', None, '1920x1080'),
    ('test_images/test_01-1680_full.jpg', (609, 417), '1680x1050'),
]

def run(img_path, resolution, show_graphs=False):
    if resolution not in SUBREGION.keys():
        raise TypeError('Resolution not supported.')
    full_map = cv.imread('full_map.png', 0)
    full_input = cv.imread(img_path, 0)

    x1, x2, y1, y2 = SUBREGION[resolution]
    test_sq = full_input[y1:y2, x1:x2]

    # cv.imshow('cropped', test_sq)
    # cv.waitKey(0)
    test_sq = cv.resize(test_sq, TEST_SIZE)
    w, h = TEST_SIZE

    methods = ['cv.TM_CCOEFF', 'cv.TM_CCOEFF_NORMED',
            'cv.TM_CCORR_NORMED', 'cv.TM_SQDIFF', 'cv.TM_SQDIFF_NORMED']

    results = Counter()
    print(img_path)
    for meth in methods:
        template = full_map.copy()
        img = test_sq.copy()
        method = eval(meth)
        # Apply template Matching
        res = cv.matchTemplate(img, template, method)
        min_val, max_val, min_loc, max_loc = cv.minMaxLoc(res)
        # If the method is TM_SQDIFF or TM_SQDIFF_NORMED, take minimum
        if method in [cv.TM_SQDIFF, cv.TM_SQDIFF_NORMED]:
            top_left = min_loc
        else:
            top_left = max_loc
        bottom_right = (top_left[0] + w, top_left[1] + h)
        cv.rectangle(template, top_left, bottom_right, 255, 5)
        res_x, res_y = int((top_left[0] + bottom_right[0])/2), int((top_left[1] + bottom_right[1]) /2)
        print(res_x, res_y, meth)
        results[(res_x, res_y)] += 1
        if meth == 'cv.TM_CCOEFF' and show_graphs:
            plt.subplot(121)
            plt.imshow(img, cmap='gray')
            plt.title('Input Image'), plt.xticks([]), plt.yticks([])
            plt.subplot(122)
            plt.imshow(template, cmap='gray')
            plt.title('Detected Point'), plt.xticks([]), plt.yticks([])
            plt.suptitle(meth)
            plt.show()
    if len(results) > 2:
        print('No Consensus')
        final_result = None
    else:
        final_result = results.most_common()[0][0]
        print('Consensus reached:', final_result)
    print('')
    return final_result


    

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
    for img_path, result, resolution in TESTS:
        if not result == 'skip':
            assert run(img_path, resolution) == result
        else:
            print(run(img_path, resolution, show_graphs=True))


# https://docs.opencv.org/trunk/d4/dc6/tutorial_py_template_matching.html