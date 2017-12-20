import cv2 as cv
from PIL import Image, ImageGrab
import numpy as np
import matplotlib.pyplot as plt

RESOLUTION = '1920x1080'

TEST_FULL_SIZE = (110, 110)
MAP_FULL_SIZE = (896, 896)

SUBREGION = {
    '1920x1080': (1615, 1895, 25, 305),
}

TESTS = [
    ('test_images/test_01_full.jpg', (206, 557)),
    ('test_images/test_02_full.jpg', (491, 557)),
    ('test_images/test_03_full.jpg', (545, 485)),
    ('test_images/test_04_full.jpg', (520, 373)),
    ('test_images/test_05_full.jpg', (425, 401)),
    ('test_images/test_06_full.jpg', (499, 325)),
    ('test_images/test_07_full.jpg', (576, 307)),
]

def run():
    full_map = cv.imread('full_map.png', 0)
    full_input = cv.imread('test_images/test_07_full.jpg', 0)

    x1, x2, y1, y2 = SUBREGION[RESOLUTION]
    test_sq = full_input[y1:y2, x1:x2]

    cv.imshow('cropped', test_sq)
    cv.waitKey(0)
    # test_sq = cv.imread('tsmap_region01.png', 0)
    test_sq = cv.resize(test_sq, TEST_FULL_SIZE)
    w, h = TEST_FULL_SIZE

    methods = ['cv.TM_CCOEFF',]
     # 'cv.TM_CCOEFF_NORMED', 'cv.TM_CCORR',
     #        'cv.TM_CCORR_NORMED', 'cv.TM_SQDIFF', 'cv.TM_SQDIFF_NORMED']

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
        print(int((top_left[0] + bottom_right[0])/2), int((top_left[1] + bottom_right[1]) /2))
        plt.subplot(121)
        plt.imshow(img, cmap='gray')
        plt.title('Input Image'), plt.xticks([]), plt.yticks([])
        plt.subplot(122)
        plt.imshow(template, cmap='gray')
        plt.title('Detected Point'), plt.xticks([]), plt.yticks([])
        plt.suptitle(meth)
        plt.show()

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
    run()
