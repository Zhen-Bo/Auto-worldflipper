import numpy as np
from cv2 import cv2


def ORB(template_gray, target_gray, debug=False):
    orb = cv2.ORB_create()

    kp1, des1 = orb.detectAndCompute(template_gray, None)
    kp2, des2 = orb.detectAndCompute(target_gray, None)

    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = bf.match(des1, des2)
    matches = sorted(matches, key=lambda x: x.distance)
    good_matches = matches[:10]

    src_pts = np.float32(
        [kp1[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
    dst_pts = np.float32(
        [kp2[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)
    M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
    matchesMask = mask.ravel().tolist()
    h, w = template_gray.shape[:2]
    pts = np.float32([[0, 0], [0, h-1], [w-1, h-1], [w-1, 0]]
                     ).reshape(-1, 1, 2)

    dst = cv2.perspectiveTransform(pts, M)

    dst = np.int32(dst)
    pos = [(dst[0][0][0].T+dst[2][0][0].T)/2,
           (dst[0][0][1].T+dst[2][0][1].T)/2]
    if debug:
        dst += (w, 0)  # adding offset
        draw_params = dict(matchColor=(0, 255, 0),  # draw matches in green color
                           singlePointColor=None,
                           matchesMask=matchesMask,  # draw only inliers
                           flags=2)
        img3 = cv2.drawMatches(
            template_gray, kp1, target_gray, kp2, good_matches, None, **draw_params)
        img3 = cv2.polylines(img3, [np.int32(dst)], True,
                             (0, 0, 255), 3, cv2.LINE_AA)
        cv2.imwrite(
            '{}/image.png'.format("C:/Users/Paver/Desktop/GIT/flipper/EXAMPLE"), img3)
    return pos


def sift(template_gray, target_gray, debug=False, filename="SIFT_image"):
    try:
        sift = cv2.SIFT_create()
        kp1, des1 = sift.detectAndCompute(template_gray, None)
        kp2, des2 = sift.detectAndCompute(target_gray, None)

        FLANN_INDEX_KDTREE = 1
        index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
        search_params = dict(checks=50)

        flann = cv2.FlannBasedMatcher(index_params, search_params)
        matches = flann.knnMatch(des1, des2, k=2)
        goodMatch = []
        for m, n in matches:
            if m.distance < 0.50*n.distance:
                goodMatch.append(m)
        src_pts = np.float32(
            [kp1[m.queryIdx].pt for m in goodMatch]).reshape(-1, 1, 2)
        dst_pts = np.float32(
            [kp2[m.trainIdx].pt for m in goodMatch]).reshape(-1, 1, 2)
        M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
        h, w = template_gray.shape[:2]
        pts = np.float32([[0, 0], [0, h-1], [w-1, h-1], [w-1, 0]]
                         ).reshape(-1, 1, 2)
        dst = cv2.perspectiveTransform(pts, M)

        dst = np.int32(dst)
        pos = [(dst[0][0][0].T+dst[2][0][0].T)/2,
               (dst[0][0][1].T+dst[2][0][1].T)/2]
        if debug:
            matchesMask = mask.ravel().tolist()
            dst += (w, 0)  # adding offset
            draw_params = dict(matchColor=(0, 255, 0),  # draw matches in green color
                               singlePointColor=None,
                               matchesMask=matchesMask,  # draw only inliers
                               flags=2)
            img3 = cv2.drawMatches(
                template_gray, kp1, target_gray, kp2, goodMatch, None, **draw_params)
            img3 = cv2.polylines(img3, [np.int32(dst)], True,
                                 (0, 0, 255), 3, cv2.LINE_AA)
            cv2.imshow('{}.png'.format(filename), img3)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        return pos
    except:
        return False


def match_template(template, target, debug=False):
    find_height, find_width = template.shape[:2:]
    result = cv2.matchTemplate(
        target, template, cv2.TM_CCOEFF_NORMED)
    if debug:
        cv2.imshow("template", template)
        cv2.imshow("target", target)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    reslist = cv2.minMaxLoc(result)
    if debug:
        cv2.rectangle(target, reslist[3], (
            reslist[3][0]+find_width, reslist[3][1]+find_height), color=(0, 250, 0), thickness=2)
        cv2.imwrite('image.png', target)
    if reslist[1] > 0.7:
        if debug:
            print("[Detect]acc rate:", round(reslist[1], 2))
            cv2.imwrite('image.png', target)
        pos = [reslist[3][0]+find_width/2, reslist[3][1]+find_height/2]
        return pos
    return False
