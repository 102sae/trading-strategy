import sys
import math
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QAxContainer import *
from PyQt5.QtWidgets import *
import pandas as pd
import GiExpertControl as giLogin
import GiExpertControl as giTop50Show
import GiExpertControl as giJongmokRealTime
from pythonUI import Ui_MainWindow
import time
import datetime

RTOCX1 = giJongmokRealTime.NewGiExpertModule()

main_ui = Ui_MainWindow()

class indiWindow(QMainWindow):

    def get_date(self):
        today = datetime.date.today()
        date_string = today.strftime("%Y%m%d")
        return date_string


    # UI 선언
    def __init__(self):
        super().__init__()
        self.setWindowTitle("IndiExample")
        giTop50Show.SetQtMode(True)
        giTop50Show.RunIndiPython()
        giLogin.RunIndiPython()
        giTop50Show.RunIndiPython()
        self.rqidD = {}
        main_ui.setupUi(self)      

        main_ui.pushButton.clicked.connect(self.buy_stock)
        main_ui.pushButton_2.clicked.connect(self.chegyeol_show)
        main_ui.pushButton_3.clicked.connect(self.sell_stock)
        main_ui.pushButton_4.clicked.connect(self.show_silsigan_jango)

        giTop50Show.SetCallBack('ReceiveData', self.giTop50Show_ReceiveData)
        RTOCX1.SetCallBack('ReceiveRTData', self.RTOCX1_ReceiveRTData)
        
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

        #시작하자마자 TOP50 출력
        TR_Name = "TR_1505_07"  
        ret = giTop50Show.SetQueryName(TR_Name)   
        ret = giTop50Show.SetSingleData(0,"0")
        ret = giTop50Show.SetSingleData(1,"0")
        rqid = giTop50Show.RequestData()
        print(type(rqid))

        print('Request Data rqid: ' + str(rqid))
        self.rqidD[rqid] = TR_Name                  

    def buy_stock(self):
        gaejwa_text = main_ui.textEdit.toPlainText()
        PW_text = main_ui.textEdit_2.toPlainText()
        jongmok_code = main_ui.textEdit_3.toPlainText()
        jumun_suryang = main_ui.textEdit_4.toPlainText()

        print(gaejwa_text,PW_text,jongmok_code,jumun_suryang)
        TR_Name = "SABA101U1"          
        ret= giTop50Show.SetQueryName(TR_Name)  
        ret = giTop50Show.SetSingleData(1,"01")#계좌 상품(항상01)
        ret = giTop50Show.SetSingleData(2,PW_text)#계좌 비밀번호
        ret = giTop50Show.SetSingleData(0,gaejwa_text)#계좌번호
        ret = giTop50Show.SetSingleData(3,"")#계좌 관리부점코드
        ret = giTop50Show.SetSingleData(4,"")#시장거래구분
        ret = giTop50Show.SetSingleData(5,"0")#선물대용매도여부
        ret = giTop50Show.SetSingleData(6,"00")#신용거래구분
        ret = giTop50Show.SetSingleData(7,"2") #매도/매수 구분
        ret = giTop50Show.SetSingleData(8,jongmok_code)#종목코드
        ret = giTop50Show.SetSingleData(9,jumun_suryang)#주문수량
        ret = giTop50Show.SetSingleData(10,"")#주문가격
        ret = giTop50Show.SetSingleData(11,"1")#정규시간외구분코드
        ret = giTop50Show.SetSingleData(12,"1")#시장가
        ret = giTop50Show.SetSingleData(13,"0")#주문조건코드
        ret = giTop50Show.SetSingleData(14,"0")#신용대출통합주문구분코드
        ret = giTop50Show.SetSingleData(15,"")#신용대출일자
        ret = giTop50Show.SetSingleData(16,"")#원주문번호
        ret = giTop50Show.SetSingleData(17,"") 
        ret = giTop50Show.SetSingleData(18,"")
        ret = giTop50Show.SetSingleData(19,"")
        ret = giTop50Show.SetSingleData(20,"")#프로그램매매여부
        ret = giTop50Show.SetSingleData(21,"Y")#결과메세지처리여부
        
        try:
            rqid = giTop50Show.RequestData()
            print(type(rqid))
            print('Request Data rqid: ' + str(rqid))
            self.rqidD[rqid] = TR_Name
        except Exception as e:
            print(f"Error in RequestData: {e}")
            rqid = None  # 또는 다른 초기값으로 설정
    
        print(type(rqid))
        print('Request Data rqid: ' + str(rqid))
        self.rqidD[rqid] = TR_Name

    #체결 내역 조회
    def chegyeol_show(self):
        TR_Name = "SABA231Q1"             
        ret = giTop50Show.SetQueryName(TR_Name)
        gaejwa_text = main_ui.textEdit.toPlainText()
        PW_text = main_ui.textEdit_2.toPlainText()

        ret = giTop50Show.SetSingleData(0,self.get_date()) #매매일자
        ret = giTop50Show.SetSingleData(1,gaejwa_text) #계좌번호
        ret = giTop50Show.SetSingleData(2,PW_text) #비밀번호
        ret = giTop50Show.SetSingleData(3,"00") #장구분
        ret = giTop50Show.SetSingleData(4,"0") #체결구분- 미체결/체결 구분없이 조회
        ret = giTop50Show.SetSingleData(5,"1") #건별구분
        ret = giTop50Show.SetSingleData(6,"*") #입력종목코드
        ret = giTop50Show.SetSingleData(7,"") #계계좌상품코드
        ret = giTop50Show.SetSingleData(8,"Y") #작업구분
        try:
            rqid = giTop50Show.RequestData()
            print("++++++++++++++++++++++++++")
            print(type(rqid))
            print('Request Data rqid: ' + str(rqid))
            self.rqidD[rqid] = TR_Name
        except Exception as e:
            print(f"Error in RequestData: {e}")
            rqid = None

    #실시간 잔고 받아오기
    def show_silsigan_jango(self):
        TR_Name = "AD"             
        print("===================실시간=====================")
        rqid = RTOCX1.RequestRTReg("AD","*")
        print(type(rqid))
        print('Request Data rqid: ' + str(rqid))        

    #자동 매도 신청
    def sell_stock(self):
        gaejwa_text = main_ui.textEdit.toPlainText()
        PW_text = main_ui.textEdit_2.toPlainText()
        jongmok_code = main_ui.textEdit_3.toPlainText()
        jumun_suryang = main_ui.textEdit_4.toPlainText()

        print(gaejwa_text,PW_text,jongmok_code,jumun_suryang)
        TR_Name = "SABA101U1"      
        ret= giTop50Show.SetQueryName(TR_Name)  
        ret = giTop50Show.SetSingleData(1,"01")#계좌 상품(항상01)
        ret = giTop50Show.SetSingleData(2,PW_text)#계좌 비밀번호
        ret = giTop50Show.SetSingleData(0,gaejwa_text)#계좌번호
        ret = giTop50Show.SetSingleData(3,"")#계좌 관리부점코드
        ret = giTop50Show.SetSingleData(4,"")#시장거래구분
        ret = giTop50Show.SetSingleData(5,"0")#선물대용매도여부
        ret = giTop50Show.SetSingleData(6,"00")#신용거래구분
        ret = giTop50Show.SetSingleData(7,"1") #매도/매수 구분
        ret = giTop50Show.SetSingleData(8,jongmok_code)#종목코드
        ret = giTop50Show.SetSingleData(9,jumun_suryang)#주문수량
        ret = giTop50Show.SetSingleData(10,"")#주문가격
        ret = giTop50Show.SetSingleData(11,"1")#정규시간외구분코드
        ret = giTop50Show.SetSingleData(12,"1")#시장가
        ret = giTop50Show.SetSingleData(13,"0")#주문조건코드
        ret = giTop50Show.SetSingleData(14,"0")#신용대출통합주문구분코드
        ret = giTop50Show.SetSingleData(15,"")#신용대출일자
        ret = giTop50Show.SetSingleData(16,"")#원주문번호
        ret = giTop50Show.SetSingleData(17,"") 
        ret = giTop50Show.SetSingleData(18,"")
        ret = giTop50Show.SetSingleData(19,"")
        ret = giTop50Show.SetSingleData(20,"")#프로그램매매여부
        ret = giTop50Show.SetSingleData(21,"Y")#결과메세지처리여부
        
        try:
            rqid = giTop50Show.RequestData()
            print(type(rqid))
            print('Request Data rqid: ' + str(rqid))
            self.rqidD[rqid] = TR_Name
        except Exception as e:
            print(f"Error in RequestData: {e}")
            rqid = None  # 또는 다른 초기값으로 설정
    
        print(type(rqid))
        print('Request Data rqid: ' + str(rqid))
        self.rqidD[rqid] = TR_Name

    def RTOCX1_ReceiveRTData(self,giCtrl,RealType):
        if RealType == "AD":
            main_ui.tableWidget_3.insertRow(main_ui.tableWidget_2.rowCount())
            final_rowCount = main_ui.tableWidget_3.rowCount() - 1
            main_ui.tableWidget_3.setItem(final_rowCount,0,QTableWidgetItem(str(giCtrl.GetSingleData(2))))#종목코드
            main_ui.tableWidget_3.setItem(final_rowCount,1,QTableWidgetItem(str(giCtrl.GetSingleData(3))))#종목명
            main_ui.tableWidget_3.setItem(final_rowCount,2,QTableWidgetItem(str(giCtrl.GetSingleData(6))))#잔고수량
            main_ui.tableWidget_3.setItem(final_rowCount,3,QTableWidgetItem(str(giCtrl.GetSingleData(7))))#평균단가
            main_ui.tableWidget_3.setItem(final_rowCount,2,QTableWidgetItem(str(giCtrl.GetSingleData(17))))#현재가
            main_ui.tableWidget_3.setItem(final_rowCount,3,QTableWidgetItem(str(giCtrl.GetSingleData(13))))#손익률

    


    def giTop50Show_ReceiveData(self,giCtrl,rqid):
        print("in receive_Data:",rqid)
        print('recv rqid: {}->{}\n'.format(rqid, self.rqidD[rqid]))

        TR_Name = self.rqidD[rqid]
        tr_data_output = []
        
        print("TR_name : ",TR_Name)

        if TR_Name == "TR_1505_07":
            nCnt = giCtrl.GetMultiRowCount()
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
        #조회
        elif TR_Name == "SABA231Q1":
            nCnt = giCtrl.GetMultiRowCount()
            print("++++++++++++++++++++++++++++++++------------+")
            print(nCnt)
            for i in range(nCnt):
                raw_time = giCtrl.GetMultiData(i, 22)
                structured_time = time.strptime(raw_time, "%H%M%S")
                formatted_time = time.strftime("%H:%M:%S", structured_time)


                tr_data_output.append([])
                main_ui.tableWidget_2.setItem(i,0,QTableWidgetItem(str(giCtrl.GetMultiData(i, 0)))) #주문번호
                main_ui.tableWidget_2.setItem(i,1,QTableWidgetItem(str(giCtrl.GetMultiData(i, 14))))#종목명
                main_ui.tableWidget_2.setItem(i,2,QTableWidgetItem(str(giCtrl.GetMultiData(i, 15))))#주문수량
                main_ui.tableWidget_2.setItem(i,3,QTableWidgetItem(str(giCtrl.GetMultiData(i, 16))))#주문단가
                main_ui.tableWidget_2.setItem(i,4,QTableWidgetItem(str(giCtrl.GetMultiData(i, 24))))#체결수량
                main_ui.tableWidget_2.setItem(i,5,QTableWidgetItem(str(giCtrl.GetMultiData(i, 25))))#체결단가
                main_ui.tableWidget_2.setItem(i, 6, QTableWidgetItem(str(formatted_time)))#체결시간
                main_ui.tableWidget_2.setItem(i,7,QTableWidgetItem(str(giCtrl.GetMultiData(i, 26))))#미체결수량
               
        #매수
        elif TR_Name == "SABA101U1":

            try:
                print("=========================")
                print("주문번호" + giCtrl.GetMultiRowCount())
            except Exception as e:
                error_message = "에러 발생"
                print(error_message)  

                    

                       
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    IndiWindow = indiWindow()    
    IndiWindow.show()
    app.exec_()
    
