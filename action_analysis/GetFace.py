import cv2
import numpy as np
def getface(img0,x1,y1,x2,y2,lastface_toward):

    imgYCRCB = cv2.cvtColor(img0,cv2.COLOR_BGR2YCR_CB)
    imgshow = img0.copy()


    skinCrCbHist = np.zeros((256,256), dtype= np.uint8 )
    cv2.ellipse(skinCrCbHist, (113, 155), (23, 15), 43, 0, 360, (255, 255, 255), -1)

    miny=y2
    maxy=0
    sum=0
    for i in range(y1,y2):
        for j in range(x1,x2):
            Cr=imgYCRCB[i,j,1]
            Cb = imgYCRCB[i, j, 2]

            if skinCrCbHist[int(Cr),int(Cb)]>0:

                if i<miny:
                    miny=i
                if i>maxy:
                    maxy=i
                sum=sum+1
                imgshow[i,j,0]=0
                imgshow[i, j, 1] = 0
                imgshow[i, j, 2] = 0

    if (x2-x1)*(y2-y1)>0:
        face_radio=sum/((x2-x1)*(y2-y1))
        cv2.putText(imgshow, str('%.3f'%face_radio), (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 1.3, (255, 0, 255), 1,
                    cv2.LINE_AA)
        if face_radio>=0.3:
            face_toward=0
        elif face_radio>=0.10:
            face_toward=1
        else:
            face_toward=2
    else:
        face_toward=lastface_toward
        face_radio=0
    return sum,miny,maxy,face_toward,face_radio








