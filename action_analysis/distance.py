import numpy as np
def getDD(State,pUI):
    x1, y1, x2, y2, S, miny, maxy = State[0], State[1], State[2], State[3], State[4], State[5], State[6]
    if pUI.F==0:
        return 0
    d = 0.20 / (maxy - miny) * pUI.F
    return d
def getdis(lastState,State,pUI):
    bS=0

    lx1, ly1, lx2, ly2, lS,lminy,lmaxy = lastState[0], lastState[1], lastState[2], lastState[3], lastState[4],lastState[5],lastState[6]
    x1,y1,x2,y2,S,miny,maxy=State[0],State[1],State[2],State[3],State[4],State[5],State[6]

    lcx=(lx1+lx2)//2
    lcy=(ly1+ly2)//2
    cx=(x1+x2)//2
    cy=(y1+y2)//2


    if pUI.W>0 and pUI.L>0 and pUI.F==0:
        pUI.F=pUI.L / 0.20 * (maxy - miny+1)

    if pUI.F==0:
        return 0

    f=pUI.F
    ld=0.20/(lmaxy-lminy)*f
    d=0.20/(maxy-miny)*f
    Dy=np.abs(ld-d)

    Dx=0
    L=np.abs(cx-lcx)-pUI.W*f*(max(ld,d)-min(ld,d))/(d*ld)
    if L>0:
      Dx=max(ld,d)/f*L


    if Dy<0.5:
        Dy=0
    if Dx<0.5:
        Dx=0


    return Dx+Dy



