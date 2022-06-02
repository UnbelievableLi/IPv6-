T=10
def action(pointlist,face_toward,d,pUI):
    if face_toward==2:
        if d<pUI.L*0.9:
            return 0
        if pointlist[15][1]<=pointlist[13][1]:
            return 1
        if pointlist[16][1]<=pointlist[14][1]:
            return 1
    else:
        cy=(pointlist[12][1]+pointlist[11][1]+pointlist[24][1]+pointlist[23][1])//4
        if pointlist[13][1] <= cy:
           if pointlist[15][1]<=pointlist[13][1]:
               return 2
        if pointlist[14][1] <= cy:
            if pointlist[16][1]<=pointlist[14][1]:
               return 2
    return 0



