import cv2
import mediapipe as mp
from pathlib import Path
import os
import sys
import numpy as np
import random
import Action
import distance
import torch
import GetFace
from models.common import DetectMultiBackend
from utils.general import (non_max_suppression, scale_coords)
from utils.torch_utils import select_device, time_sync
from utils.augmentations import  letterbox

FILE = Path(__file__).resolve()
ROOT = FILE.parents[0]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))
ROOT = Path(os.path.relpath(ROOT, Path.cwd()))

mpPose = mp.solutions.pose
mpFace = mp.solutions.face_detection
pose = mpPose.Pose(static_image_mode=False,
                   upper_body_only=False,
                   smooth_landmarks=True,
                   min_detection_confidence=0.5,
                   min_tracking_confidence=0.5)
face=mpFace.FaceDetection(0.75)
mpDraw = mp.solutions.drawing_utils

global X,P,X_last,P_last,F,H,Z,Q,R,I,Qn,Rn
X=np.mat(np.zeros((8,1)))
P=np.mat(np.zeros((8,8)))
X_last=np.mat(np.zeros((8,1)))
P_last=np.mat("10 0 0 0 0 0 0 0; 0 10 0 0 0 0 0 0; 0 0 10 0 0 0 0 0; 0 0 0 10 0 0 0 0; 0 0 0 0 10 0 0 0; 0 0 0 0 0 10 0 0; 0 0 0 0 0 0 10 0; 0 0 0 0 0 0 0 10")
F=np.mat("1 0 0 0 1 0 0 0; 0 1 0 0 0 1 0 0; 0 0 1 0 0 0 1 0; 0 0 0 1 0 0 0 1; 0 0 0 0 1 0 0 0; 0 0 0 0 0 1 0 0; 0 0 0 0 0 0 1 0; 0 0 0 0 0 0 0 1")
H=np.mat("1 0 0 0 0 0 0 0; 0 1 0 0 0 0 0 0; 0 0 1 0 0 0 0 0; 0 0 0 1 0 0 0 0")
Z=np.mat(np.zeros((4,1)))
Q=np.mat(np.zeros((8,8)))
R=np.mat(np.zeros((4,4)))
I=np.mat(np.zeros((8,8)))
for i in range(8):
    I[i,i]=1
Qn=2
Rn=1
Ty=50
Tx=40


weights = ROOT / 'best.pt'
dnn=False
half=False
data = ROOT / 'data/head.yaml'
device = 0

model = DetectMultiBackend(weights, device=select_device(device), dnn=dnn, data=data, fp16=half)
stride, names, pt = model.stride, model.names, model.pt

def getPerson(img0):
    device = 0
    conf_thres = 0.10
    iou_thres = 0.45
    classes = 0
    max_det = 1000
    imgsz = (640, 640)
    ans=[]

    img1 = letterbox(img0, imgsz, stride=stride, auto=pt)[0]
    img1 = img1.transpose((2, 0, 1))[::-1]
    img1 = np.ascontiguousarray(img1)

    im = torch.from_numpy(img1).to(device)
    im = im.half() if model.fp16 else im.float()
    im /= 255
    if len(im.shape) == 3:
        im = im[None]

    pred = model(im, augment=False, visualize=False)
    pred = non_max_suppression(pred, conf_thres, iou_thres, classes, False, max_det=max_det)
    for i, det in enumerate(pred):
        det[:, :4] = scale_coords(im.shape[2:], det[:, :4], img0.shape).round()
        for *xyxy, conf, cls in reversed(det):
            ans.append(xyxy)

    return ans

def getTeacher(Person,px1,py1,px2,py2,x1,y1,x2,y2,img0):
    if px1==py1==px2==py2==0:
        mx1, my1, mx2, my2 = 0, 100000, 0, 0
        S = 0
        for [nnx1, nny1, nnx2, nny2] in Person:
            nx1, ny1, nx2, ny2=int(nnx1), int(nny1), int(nnx2), int(nny2)
            if ny1<my1:
                mx1, my1, mx2, my2 = nx1, ny1, nx2, ny2
        if mx1==0 and my1==100000 and mx2==0 and my2==0:
            return False, mx1, my1, mx2, my2
        return True,mx1, my1, mx2, my2

    else:
        mx1, my1, mx2, my2 = 0, 0, 0, 0
        S = 0
        for [nnx1, nny1, nnx2, nny2] in Person:
            nx1, ny1, nx2, ny2 = int(nnx1), int(nny1), int(nnx2), int(nny2)
            jx1 = max(px1, nx1)
            jy1 = max(py1, ny1)
            jx2 = min(px2, nx2)
            jy2 = min(py2, ny2)
            if jx1 < jx2 and jy1 < jy2:
                if (jx2 - jx1 + 1) * (jy2 - jy1 + 1) > S:
                    S = (jx2 - jx1 + 1) * (jy2 - jy1 + 1)
                    mx1, my1, mx2, my2 = nx1, ny1, nx2, ny2

        if S == 0:
            return False, x1, y1, x2, y2
        else:
            return True, mx1, my1, mx2, my2


def Kalman(x1,y1,x2,y2,Number):
    global X, P, X_last, P_last, F, H, Z, Q, R, I, Qn, Rn
    if Number==1:
        X_last[0, 0] = x1
        X_last[1, 0] = y1
        X_last[2, 0] = x2
        X_last[3, 0] = y2
        X_last[4, 0] = 0
        X_last[5, 0] = 0
        X_last[6, 0] = 0
        X_last[7, 0] = 0

    Z[0, 0] = x1
    Z[1, 0] = y1
    Z[2, 0] = x2
    Z[3, 0] = y2
    for i in range(8):
        Q[i, i] = np.sqrt(Qn) * random.random()
    for i in range(2):
        R[i, i] = np.sqrt(Rn) * random.random()
    for i in range(2,4):
        R[i, i] = np.sqrt(Rn)*10 * random.random()
    X = F * X_last
    P = F * P_last * F.T + Q

    Y = Z - H * X
    S = H * P * H.T + R
    K = P * H.T * S.I

    X_last = X + K * Y
    P_last = (I - K * H) * P

    return int(X[0,0]),int(X[1,0]),int(X[2,0]),int(X[3,0])

def Run(pUI):
    filepath = str(ROOT / "vedio"/pUI.Vname)
    print(filepath)
    cap = cv2.VideoCapture(filepath)
    rate = cap.get(5)
    print(rate)
    pointlist = []
    HasTeacher = False
    x1, y1, x2, y2 = 0, 0, 0, 0
    Number = 0
    Frameofact = np.zeros((3))
    Nameofact = ["无", "板书", "比划"]
    Nameoftoward = ["正脸", "侧脸", "背面"]
    framenum = 0
    len=0
    px1,py1,px2,py2=0,0,0,0
    lastface_toward=0
    Nface=0
    lastframe=0
    changetime=0

    while True:
        success, img0 = cap.read()
        if not success:
            break
        framenum = framenum + 1
        if framenum >10:
            break
        LL2 = np.array(img0).shape[0]
        LL1 = np.array(img0).shape[1]

    framenum = 0
    while True:
        if pUI.stopEvent.is_set():
            pUI.displayEvent.wait()
        ok, img00 = cap.read()


        a = 1.3
        O = img00 * float(a)
        O[O > 255] = 255
        O = np.round(O)
        O = O.astype(np.uint8)
        img0=O.copy()

        Number=Number+1
        if not ok:
            break

        Person = getPerson(img0)


        mark, x1, y1, x2, y2 = getTeacher(Person,px1,py1,px2,py2,x1,y1,x2,y2,img0)
        if mark==True:
            px1,py1,px2,py2=Kalman(x1, y1, x2, y2, Number)
            HasTeacher=True
        else:
            px1, py1, px2, py2=0,0,0,0
            HasTeacher=False

        cv2.rectangle(img0, (x1, y1), (x2, y2), (0, 0, 255), 2)
        if HasTeacher:


            face_S,face_min,face_max,face_toward,face_rate= GetFace.getface(img0, x1, y1, x2, y2, lastface_toward)
            #cv2.putText(img0,Nameoftoward[face_toward], (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 1.3, (255, 0, 255),1,cv2.LINE_AA)
            str(Nameoftoward[face_toward])
            lenx = int((x2 - x1 + 1) * 7.18/2)
            leny = int((y2 - y1 + 1) * 3)
            xx1 = x1- lenx+int((x2 - x1 + 1)/2)

            yy1 = y1 -  int((y2 - y1 + 1))
            xx2 = x2+ lenx-int((x2 - x1 + 1)/2)
            yy2 = y1 + leny
            if xx1 < 0:
                xx1 = 0
            if yy1 < 0:
                yy1 = 0
            if xx2 >= LL1:
                xx2 = LL1 - 1
            if yy2 >= LL2:
                yy2 = LL2 - 1

            img1 = img0[yy1:yy2, xx1:xx2]

            imgRGB = cv2.cvtColor(img1, cv2.COLOR_BGR2RGB)
            results = pose.process(imgRGB)
            L2 = np.array(imgRGB).shape[0]
            L1 = np.array(imgRGB).shape[1]

            #cv2.rectangle(img0, (xx1, yy1), (xx2, yy2), (255, 0, 0), 2)

            if results.pose_landmarks:
                framenum = framenum + 1
                pointlist = []
                for id, point in enumerate(results.pose_landmarks.landmark):
                    x, y = int(point.x * L1), int(point.y * L2)
                    pointlist.append([x, y, point.z, point.visibility])

                #mpDraw.draw_landmarks(img1, results.pose_landmarks, mp.solutions.holistic.POSE_CONNECTIONS)
                act = Action.action(pointlist,face_toward,distance.getDD([x1,y1,x2,y2,face_S, face_min, face_max],pUI),pUI)
                #cv2.putText(img0, str(Nameofact[act]), (xx1, yy1), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 255), 1,cv2.LINE_AA)


                Frameofact[act]+=1


            if pUI.isDemarcate:
                if face_toward==0:
                    Nface = Nface + 1
                    if Nface==1 or Number-lastframe>=50:
                        State = [x1, y1, x2, y2, face_S, face_min, face_max]
                        if Nface == 1:
                            lastState = State
                            lastframe = Number
                        len = len + distance.getdis(lastState,State,pUI)
                        changetime=Number
                        lastState = State
                        lastframe = Number




        pUI.Display(img0)
        pUI.OutputS(face_toward,act,len,Frameofact,rate,changetime,Number)