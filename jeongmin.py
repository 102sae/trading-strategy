import sys
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QAxContainer import *
from PyQt5.QtWidgets import *
import pandas as pd
import GiExpertControl as giLogin
import GiExpertControl as giTop50Show
from pythonUI2 import Ui_MainWindow

main_ui = Ui_MainWindow()

class indiWindow(QMainWindow):
    # UI 선언
    def __init__(self):
        super().__init__()
        self.setWindowTitle("IndiExample")
        giTop50Show.SetQtMode(True)
        giTop50Show.RunIndiPython()
        giLogin.RunIndiPython()
        self.rqidD = {}
        main_ui.setupUi(self)      

        main_ui.pushButton.clicked.connect(self.pushButton_clicked)
        giTop50Show.SetCallBack('ReceiveData', self.giTop50Show_ReceiveData)

        print(giLogin.GetCommState())
        if giLogin.GetCommState() == 0: # 정상
            print("")        
        elif  giLogin.GetCommState() == 1: # 비정상
        #본인의 ID 및 PW 넣으셔야 합니다
            login_return = giLogin.StartIndi('234121','a0000858!','', 'C:\\SHINHAN-i\\indi\\GiExpertStarter.exe')
            if login_return == True:
                print("INDI 로그인 정보","INDI 정상 호출")
            else:
                print("INDI 로그인 정보","INDI 호출 실패") 

        TR_Name = "TR_1505_07"  
        ret = giTop50Show.SetQueryName(TR_Name)   
        ret = giTop50Show.SetSingleData(0,"0")
        ret = giTop50Show.SetSingleData(1,"0")
        rqid = giTop50Show.RequestData()
        print(type(rqid))
        print('Request Data rqid: ' + str(rqid))
        self.rqidD[rqid] = TR_Name                  

    def pushButton_clicked(self):
        gaejwa_text = main_ui.textEdit.toPlainText()
        PW_text = main_ui.textEdit_2.toPlainText()
        money_text = main_ui.textEdit_3.toPlainText()
        sueik_percent_text = main_ui.textEdit_4.toPlainText()

        TR_Name = "SABA101U1"          
        ret = giTop50Show.SetQueryName(TR_Name)          
        #print(giJongmokTRShow.GetErrorCode())
        #print(giJongmokTRShow.GetErrorMessage())
        ret = giTop50Show.SetSingleData(0,gaejwa_text)
        ret = giTop50Show.SetSingleData(1,"01")
        ret = giTop50Show.SetSingleData(2,PW_text)
        rqid = giTop50Show.RequestData()
        print(type(rqid))
        print('Request Data rqid: ' + str(rqid))
        self.rqidD[rqid] = TR_Name    


    def giTop50Show_ReceiveData(self,giCtrl,rqid):
        print("in receive_Data:",rqid)
        print('recv rqid: {}->{}\n'.format(rqid, self.rqidD[rqid]))
        TR_Name = self.rqidD[rqid]
        tr_data_output = []
        output = []

        print("TR_name : ",TR_Name)
        if TR_Name == "TR_1505_07":
            nCnt = giCtrl.GetMultiRowCount()
            print("c")
            for i in range(0, nCnt):
                tr_data_output.append([])
                main_ui.tableWidget.setItem(i,0,QTableWidgetItem(str(giCtrl.GetMultiData(i, 0))))
                main_ui.tableWidget.setItem(i,1,QTableWidgetItem(str(giCtrl.GetMultiData(i, 1))))
                main_ui.tableWidget.setItem(i,2,QTableWidgetItem(str(giCtrl.GetMultiData(i, 2))))
                main_ui.tableWidget.setItem(i,3,QTableWidgetItem(str(giCtrl.GetMultiData(i, 3))))
                main_ui.tableWidget.setItem(i,4,QTableWidgetItem(str(giCtrl.GetMultiData(i, 4))))
                main_ui.tableWidget.setItem(i,5,QTableWidgetItem(str(giCtrl.GetMultiData(i, 5))))
                main_ui.tableWidget.setItem(i,6,QTableWidgetItem(str(giCtrl.GetMultiData(i, 6))))
                main_ui.tableWidget.setItem(i,7,QTableWidgetItem(str(giCtrl.GetMultiData(i, 7))))
                main_ui.tableWidget.setItem(i,8,QTableWidgetItem(str(giCtrl.GetMultiData(i, 8))))
                for j in range(0,9):
                    tr_data_output[i].append(giCtrl.GetMultiData(i, j))
            print(type(tr_data_output))
                       
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    IndiWindow = indiWindow()    
    IndiWindow.show()
    app.exec_()
    
