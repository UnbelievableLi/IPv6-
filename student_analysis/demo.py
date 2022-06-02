from detector.AIDetector_pytorch import Detector
from classification.classification import Classification
from process import *
from posture.pose_demo import pose_estimate
import cv2
import os
from PIL import Image


if __name__ == '__main__':
    name = 'demo'
    inputpath = input('Please input the file path: ')
    det = Detector()
    classfication = Classification()
    # cap = cv2.VideoCapture('test_videos/test1.mp4')
    cap = cv2.VideoCapture(inputpath)
    fps = int(cap.get(5))
    t = int(1000 / fps)

    videoWriter = None

    hand_num = 0
    active_count = 0
    frame_count = 0
    pre2_hand = []
    pre_hand = []
    interval = 10
    result2plot = []

    while True:
        _, im = cap.read()
        if im is None:
            break

        result = det.feedCap(im)

        if interval % 10 == 0:
            # crop single student
            if result['box_cls_id']:
                crop(result['frame'], result['box_cls_id'])

            pose_estimate()

            filelist = os.listdir('temp/')  # 该文件夹下所有的文件（包括文件夹）
            folder_filename_list = []

            for img in filelist:
                try:
                    image = Image.open('temp/' + img)
                except:
                    print('Open Error! Try again!')
                    continue
                else:
                    class_name = classfication.detect_image(image)
                    img_id = img.split('.')
                    folder_filename_list.append([class_name, img_id[0]])

            active = False
            for cls, stu_id in folder_filename_list:
                if cls == 'hand':
                    for cls_pre, stu_id_pre in pre_hand:
                        for cls_pre2, stu_id_pre2 in pre2_hand:
                            if stu_id == stu_id_pre == stu_id_pre2 and cls_pre == 'hand' and cls_pre2 != 'hand':
                                hand_num += 1
                                # print('hands up')

                for item in result['box_cls_id']:
                    if int(stu_id) == item[5]:
                        item[4] = cls
                    if item[4] == 'hand' or item[4] == 'stand':
                        active = True
            if active:
                active_count += 1

            result2plot = result['box_cls_id']

            pre2_hand = pre_hand.copy()
            pre_hand = folder_filename_list.copy()
            frame_count += 1

        # print(result['box_cls_id'])
        img_result = plot(result['frame'], result2plot)
        interval += 1
        # print(str(active_count) + ' ' + str(frame_count))
        if videoWriter is None:
            fourcc = cv2.VideoWriter_fourcc(
                'm', 'p', '4', 'v')  # opencv3.0
            videoWriter = cv2.VideoWriter(
                'result.mp4', fourcc, fps, (img_result.shape[1], img_result.shape[0]))

        videoWriter.write(img_result)
        cv2.imshow(name, img_result)
        cv2.waitKey(t)

        if cv2.getWindowProperty(name, cv2.WND_PROP_AUTOSIZE) < 1:
            # 点x退出
            break

    cap.release()
    videoWriter.release()
    cv2.destroyAllWindows()
    print('active_rate:' + str(round(active_count/frame_count*100, 2)) + '%')
    print('hand_num:' + str(hand_num))
