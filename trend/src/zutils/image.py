# @Time   : 2018-9-10
# @Author : zxh
import numpy as np
from PIL import Image, ImageDraw
from scipy import misc
def normalization_image(image):
    image = image.astype(np.float32)
    mean = np.mean(image)
    std = np.std(image)
    std_adj = np.maximum(std, 1.0 / np.sqrt(image.size))
    image = np.multiply(np.subtract(image, mean), 1 / std_adj)
    return image

def random_rotate_image(image):
    angle = np.random.uniform(low=-10.0, high=10.0)
    return misc.imrotate(image, angle, 'bicubic')

class Polygonal:
    def __init__(self, h, w, point_list, margin = 1 / 15):
        arr = np.zeros([h, w], np.uint8)
        image = Image.fromarray(arr)
        draw = ImageDraw.Draw(image)
        xy_list = list()
        for y, x in point_list:
            xy_list.append((x, y))
        draw.polygon(xy_list, fill=255)

        min_h = h
        max_h = 0
        min_w = w
        max_w = 0
        for ih, iw in point_list:
            min_h = min(min_h, ih)
            max_h = max(max_h, ih)
            min_w = min(min_w, iw)
            max_w = max(max_w, iw)

        min_h = max(min_h - int (h * margin), 0)
        max_h = min(max_h + int (h * margin), h)
        min_w = max(min_w - int (w * margin), 0)
        max_w = min(max_w + int (w * margin), w)

        image01 = np.array(image)
        # misc.imsave('test.jpg', image01)
        def is_in(h, w):
            return image01[min_h + h][min_w+ w]

        def crop(image):
            # print(image.shape)
            # print(min_h, max_h, min_w, max_w)
            return image[min_h:max_h, min_w:max_w, :]

        def plus_top_left(h, w):
            return h+min_h, w+min_w


        def draw_pilimage_polygonal(pilimage, draw=None, color=(0 ,0, 255)):

            if draw is None:
                draw = ImageDraw.Draw(pilimage)
                draw.polygon(xy_list, outline=color)
                del draw
            else:
                draw.polygon(xy_list, outline=color)

        def draw_npimage_polygonal(npimage, draw=None, color=(0 ,0, 255)):

            if draw is None:
                pilimage = Image.fromarray(npimage)
                draw = ImageDraw.Draw(pilimage)
                draw.polygon(xy_list, outline=color)
                del draw
            else:
                draw.polygon(xy_list, outline=color)
            return np.array(pilimage)

        self.is_in = is_in
        self.plus_top_left = plus_top_left
        self.crop = crop
        self.draw_pilimage_polygonal = draw_pilimage_polygonal
        self.draw_npimage_polygonal = draw_npimage_polygonal



if __name__ == '__main__':
    import cv2
    from zutils.utils import relative_project_path
    image = cv2.imread(relative_project_path('data/1096.jpg'))
    p = Polygonal(image.shape[0], image.shape[1], [(0, 100), (100, 50), (100, 100)])
    # pimage = Image.fromarray(image)
    # p.draw_polygonal(pimage)
    pimage.show()


