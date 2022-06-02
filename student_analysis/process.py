import cv2


def plot(image, bboxes, line_thickness=None):
    stu_num = len(bboxes)
    cv2.putText(image, 'stu_num: ' + str(stu_num), (5, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    down_count = 0
    down_rate = 0
    # Plots one bounding box on image img
    tl = line_thickness or round(
        0.002 * (image.shape[0] + image.shape[1]) / 2) + 1  # line/font thickness
    for (x1, y1, x2, y2, cls_id, pos_id) in bboxes:
        if cls_id in ['listen']:
            color = (0, 0, 255)
        elif cls_id in ['hand', 'stand']:
            color = (0, 255, 0)
        else:
            color = (0, 0, 0)

        if cls_id == 'down':
            down_count += 1

        c1, c2 = (x1, y1), (x2, y2)
        cv2.rectangle(image, c1, c2, color, thickness=tl, lineType=cv2.LINE_AA)
        tf = max(tl - 1, 1)  # font thickness
        t_size = cv2.getTextSize(cls_id, 0, fontScale=tl / 3, thickness=tf)[0]
        c2 = c1[0] + t_size[0] - 12, c1[1] - t_size[1]
        cv2.rectangle(image, c1, c2, color, -1, cv2.LINE_AA)  # filled
        cv2.putText(image, '{} ID-{}'.format(cls_id, pos_id), (c1[0], c1[1] - 2), 0, tl / 4,
                    [225, 255, 255], thickness=tf, lineType=cv2.LINE_AA)
    if not stu_num == 0:
        down_rate = down_count/stu_num
    cv2.putText(image, 'listen_rate: ' + str(round(100-down_rate*100, 2)) + '%', (5, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    cv2.putText(image, 'down_rate: ' + str(round(down_rate*100, 2)) + '%', (5, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    return image


def crop(image, bboxes):
    for (x1, y1, x2, y2, cls_id, pos_id) in bboxes:
        cropped_img = image[y1:y2, x1:x2]
        cv2.imwrite('temp/' + str(pos_id) + '.jpg', cropped_img)