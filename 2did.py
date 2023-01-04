# -*- coding: utf-8 -*-

import time
import cv2
import numpy as np
from pylibdmtx import pylibdmtx
from PIL import Image


if __name__ == '__main__':
    img = cv2.imread('dmimg.jpg', cv2.IMREAD_UNCHANGED)
    cv2.imshow('2DID', img)

    # Select a ROI and then press SPACE or ENTER button!
    # Cancel the selection precess by pressing C button!
    x_pos, y_pos, width, height = cv2.selectROI("2DID", img, True)
    print("x position, y position: ", x_pos, y_pos)
    print('width, height: ', width, height)

    cv2.destroyAllWindows()

    userinput = input("Input 2DID Image: ")
    if not userinput:
        userinput = 'dmimg.JPG'

    img2did = Image.open(userinput)
    # img2did.show()    # original image
    print(img2did.width, img2did.height)

    one_pick_w = img2did.width / 2
    one_pick_h = img2did.height / 3

    # position = [[50, 50, one_pick_w - 100, one_pick_h - 150],
    #             [one_pick_w + 60, 50, one_pick_w * 2 - 100, one_pick_h - 150],
    #             [50, one_pick_h + 80, one_pick_w - 100, one_pick_h * 2 - 140],
    #             [one_pick_w + 65, one_pick_h + 80, one_pick_w * 2 - 100, one_pick_h * 2 - 140],
    #             [50, one_pick_h * 2 + 120, one_pick_w - 100, one_pick_h * 3 - 90],
    #             [one_pick_w + 80, one_pick_h * 2 + 120, one_pick_w * 2 - 100, one_pick_h * 3 - 90]]

    xy_pos = [[53, 64], [443, 53], [62, 475], [452, 470], [67, 879], [458, 875]]
    xp = 164
    yp = 150

    # crop(left, up, rigth, down)
    for i, pos in enumerate(xy_pos):
        # croppedimg = img2did.crop(pos)
        try:
            croppedimg = img2did.crop((pos[0], pos[1], pos[0] + xp, pos[1] + yp))
            croppedimg.show()
        except Exception as e:
            print(e)

        if i == 4:
            # pass
            croppedimg.show()   # Display cropped image
            # print("Size of cropped image: ", croppedimg.size)

        croppedimg.save('onepick.jpg')

        image = cv2.imread('onepick.jpg', cv2.IMREAD_UNCHANGED)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        ret, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        msg: list = pylibdmtx.decode(thresh)

        if len(msg) > 0:
            for d in msg:
                dmcode = d.data.decode('utf-8')     # decode bytes to string
                print(dmcode, ',', len(dmcode))
        else:
            print("recognition error")

        time.sleep(.1)
