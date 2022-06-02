import cv2
import sys
import threading
import TeacherDetect
from PyQt5.QtWidgets import QMainWindow,QPushButton,QApplication,QGridLayout,QDialog,QLabel, QLineEdit
from PyQt5.QtGui import QImage,QPixmap
Nameofact = ["无", "板书", "无"]
Nameoftoward = ["正脸", "侧脸", "背面"]

class UI(QDialog):
    def __init__(self, parent=None):
        super(UI, self).__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.setGeometry(200, 200, 400, 200)
        self.setWindowTitle('教师行为分析系统')
        self.Pin = QLabel()
        self.Path = QLineEdit()
        self.Vedio = QLabel()
        self.Lin = QLabel()
        self.SizeL = QLineEdit()
        self.Win = QLabel()
        self.SizeW = QLineEdit()
        self.SizeS = QLabel()
        self.State = QLabel()

        self.Vedio.setFixedSize(1200, 700)
        #self.Vedio.setGeometry(300, 250, 200, 220)
        #self.Vedio.setFixedSize(1200, 800)

        #self.Vedio.setScaledContents(True)


        self.start=QPushButton()
        self.start.setText('播放')
        self.start.setStyleSheet('''
                       background-color:rgb(243,210,230);
                       font-size:18px;
                       font-family:微软雅黑;
                       border-radius:5px;
                       border:2px solid rgb(255, 0, 0);
                       ''')

        self.stop=QPushButton()
        self.stop.setText('暂停')
        self.stop.setStyleSheet('''
                               background-color:rgb(243,210,230);
                               font-size:18px;
                               font-family:微软雅黑;
                               border-radius:5px;
                               border:2px solid rgb(255, 0, 0);
                               ''')

        self.demarcate = QPushButton()
        self.demarcate.setText('标定')
        self.demarcate.setStyleSheet('''
                                       background-color:rgb(243,210,230);
                                       font-size:18px;
                                       font-family:微软雅黑;
                                       border-radius:5px;
                                       border:2px solid rgb(255, 0, 0);
                                       ''')

        self.Pin.setText("输入待测视频名称：")

        self.Lin.setText("与黑板距离（单位：米）：")

        self.Win.setText("与过道距离（单位：米）：")


        self.SizeS.setText("请在第一个框中输入拍摄点到黑板的距离\n"+
                           "请在第二个框中输入拍摄点到过道的距离\n"+
                           "然后点击标定按钮进行焦距的估算")



        self.layout = QGridLayout()
        #self.layout.setSpacing(20)
        self.layout.addWidget(self.Vedio, 0, 0, 11, 1)
        self.layout.addWidget(self.Pin, 0, 1, 1, 1)
        self.layout.addWidget(self.Path, 1, 1, 1, 1)
        self.layout.addWidget(self.start, 2, 1, 1, 1)
        self.layout.addWidget(self.stop, 3, 1, 1, 1)
        self.layout.addWidget(self.Lin, 4, 1, 1, 1)
        self.layout.addWidget(self.SizeL, 5, 1, 1, 1)
        self.layout.addWidget(self.Win, 6, 1, 1, 1)
        self.layout.addWidget(self.SizeW, 7, 1, 1, 1)
        self.layout.addWidget(self.SizeS, 8, 1, 1, 1)
        self.layout.addWidget(self.demarcate, 9, 1, 1, 1)
        self.layout.addWidget(self.State, 10, 1, 1, 1)

        self.setLayout(self.layout)


class Ctl:
    def __init__(self):
        self.ui=UI()
        self.ui.show()
        self.ui.start.clicked.connect(self.Start)
        self.ui.stop.clicked.connect(self.Stop)
        self.ui.demarcate.clicked.connect(self.Demarcate)

        img0=cv2.imread('UI/white.png')
        #self.Display(img0)

        self.F=0
        self.isOpen=True
        self.displayEvent=threading.Event()
        self.displayEvent.clear()
        self.stopEvent = threading.Event()
        self.stopEvent.clear()

        self.isDemarcate = False

        self.OutputS(0,0,0,[0,0,0],1,0,0)
        self.ui.show()

    def Start(self):
        self.Vname=str(self.ui.Path.text())
        self.displayEvent.set()
        self.stopEvent.clear()
        if self.isOpen==True:
            t1=threading.Thread(target=self.Run)
            t1.start()
            self.isOpen=False

    def Stop(self):
        self.displayEvent.clear()
        self.stopEvent.set()

    def Run(self):
        TeacherDetect.Run(self)
        #TeacherAnalyse.Run(self)

    def Display(self,img):
        self.ui.Vedio.setScaledContents(True)
        qimg = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        qimg=QImage(qimg.data, qimg.shape[1], qimg.shape[0], QImage.Format_RGB888)
        self.ui.Vedio.setPixmap(QPixmap.fromImage(qimg))

    def Demarcate(self):
        self.L =float(self.ui.SizeL.text())
        self.W =float(self.ui.SizeW.text())
        self.ui.SizeS.setText("请在第一个框中输入拍摄点到黑板的距离\n"+
                           "请在第二个框中输入拍摄点到过道的距离\n"+
                           "然后点击标定按钮进行焦距的估算\n"+"焦距标定："+"完成")
        self.ui.State.setStyleSheet('''
                                                      background-color:rgb(193,216,230);
                                                      font-size:18px;
                                                      font-family:微软雅黑;
                                                      border-radius:5px;
                                                      ''')

        self.isDemarcate = True

    def OutputS(self,face,act,len,Frameofact,rate,change,Number):

        self.ui.State.setText("\n"+"脸部朝向："+Nameoftoward[face]+"\n\n"+
                           "动作类型："+Nameofact[act]+"\n\n"+
                           "当前时间：" + str(int(Number / 30 // 60)) + "分" + str(int(Number / 30 - Number / 30 // 60 * 60)) + "秒\n\n"
                           "更新时间：" + str(int(change/30//60)) + "分" + str(int(change/30-change/30//60*60)) + "秒\n\n"
                           "移动距离："+str(round(len/1,2))+"米\n\n" +
                           "板书时长："+str(int(Frameofact[1]/rate))+"秒\n"
                           )#"示意时长："+str(int(Frameofact[2]/rate))+"秒\n"

        self.ui.State.setStyleSheet('''
                                              background-color:rgb(193,216,230);
                                              font-size:18px;
                                              font-family:微软雅黑;
                                              border-radius:5px;
                                              ''')



if __name__ == "__main__":
    app = QApplication(sys.argv)
    M=Ctl()
    sys.exit(app.exec_())

