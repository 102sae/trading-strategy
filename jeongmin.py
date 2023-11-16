import sys
import os
from dotenv import load_dotenv
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QAxContainer import *
from PyQt5.QtWidgets import *
import GiExpertControl as giLogin
import GiExpertControl as giTop50Show
import GiExpertControl as giJongmokRealTime
from pythonUI import Ui_MainWindow
import time
import datetime
import telepot
import schedule

RTOCX1 = giJongmokRealTime.NewGiExpertModule()

main_ui = Ui_MainWindow()

# .env 파일 로드
load_dotenv()

# 토큰 값 가져오기
my_token = os.getenv("MY_TOKEN")

#텔레그램 id
id = 6389125198
token = my_token
bot = telepot.Bot(token)
flag = "매수"

class indiWindow(QMainWindow):


    #날짜 형식 포맷
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
        giJongmokRealTime.RunIndiPython()

        self.rqidD = {}
        main_ui.setupUi(self)      
        self.previous_chegyeol_data = []

        main_ui.pushButton.clicked.connect(self.buy_stock) #매수 주문 버튼
        main_ui.pushButton_2.clicked.connect(self.chegyeol_show) #체결 내역 버튼
        main_ui.pushButton_3.clicked.connect(self.show_jango) #실시간 잔고 버튼
        main_ui.pushButton_4.clicked.connect(self.sell_stock) # 매도 예약 버튼

        giTop50Show.SetCallBack('ReceiveData', self.giTop50Show_ReceiveData)
        RTOCX1.SetCallBack('ReceiveRTData', self.RTOCX1_ReceiveRTData)
        
        print(giLogin.GetCommState())
        if giLogin.GetCommState() == 0: # 정상
            print("")        
        elif  giLogin.GetCommState() == 1: # 비정상
        #본인의 ID 및 PW 
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

        # 주기적으로 체결 결과를 조회하는 스케쥴러 -> view_trade_history 함수를 호출하는 타이머 생성
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.chegyeol_show)
        self.timer.start(10000)  # 60초(60,000 밀리초)마다 타이머 이벤트 발생

    #매수 주문
    def buy_stock(self):
        self.flag = "매수"
        gaejwa_text = main_ui.textEdit.toPlainText()
        PW_text = main_ui.textEdit_2.toPlainText()
        jongmok_code = main_ui.textEdit_3.toPlainText()
        jumun_suryang = main_ui.textEdit_4.toPlainText()
        # jongmok_code="A005930"
        # jumun_suryang="1"
        # price=""
        TR_Name = "SABA101U1"          
        ret= giTop50Show.SetQueryName(TR_Name)  

        ret = giTop50Show.SetSingleData(0,gaejwa_text)#계좌번호
        ret = giTop50Show.SetSingleData(1,"01")#계좌 상품(항상01)
        ret = giTop50Show.SetSingleData(2,PW_text)#계좌 비밀번호
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
            print(e)
    
    #체결 내역 조회
    def chegyeol_show(self):
        TR_Name = "SABA231Q1"             
        ret = giTop50Show.SetQueryName(TR_Name)
        # gaejwa_text = main_ui.textEdit.toPlainText()
        # PW_text = main_ui.textEdit_2.toPlainText()

        ret = giTop50Show.SetSingleData(0,self.get_date()) #매매일자
        ret = giTop50Show.SetSingleData(1,"27051496084") #계좌번호
        ret = giTop50Show.SetSingleData(2,"0000") #비밀번호
        ret = giTop50Show.SetSingleData(3,"00") #장구분
        ret = giTop50Show.SetSingleData(4,"0") #체결구분- 미체결/체결 구분없이 조회
        ret = giTop50Show.SetSingleData(5,"1") #건별구분
        ret = giTop50Show.SetSingleData(6,"*") #입력종목코드
        ret = giTop50Show.SetSingleData(7,"") #계계좌상품코드
        ret = giTop50Show.SetSingleData(8,"Y") #작업구분
        try:
            rqid = giTop50Show.RequestData()
            print("+++++++++++체결 내역 조회+++++++++++++++")
            print(type(rqid))
            print('Request Data rqid: ' + str(rqid))
            self.rqidD[rqid] = TR_Name
        except Exception as e:
            print(f"Error in RequestData: {e}")
    
    #실시간 체결 받아오기
    def show_silsigan_jango(self):          
        print("===================실시간=====================")
        rqid = RTOCX1.RequestRTReg("AA","27051496084")
        print(type(rqid))
        print('Request Data rqid: ' + str(rqid))

    def show_jango(self):
        TR_Name = "SABA609Q1"             
        ret = giTop50Show.SetQueryName(TR_Name)
        # gaejwa_text = main_ui.textEdit.toPlainText()
        # PW_text = main_ui.textEdit_2.toPlainText()

        ret = giTop50Show.SetSingleData(0,"27051496084") #계좌번호
        ret = giTop50Show.SetSingleData(1,"01") #계좌번호
        ret = giTop50Show.SetSingleData(2,"0000") #비밀번호
        ret = giTop50Show.SetSingleData(3,"1") #구분 매매기준
        ret = giTop50Show.SetSingleData(4,"1") #단가구분
        ret = giTop50Show.SetSingleData(5,"0") #종목구분코드
        ret = giTop50Show.SetSingleData(6,"0") #작업구분
        try:
            rqid = giTop50Show.RequestData()
            print("+++++++++++잔고 내역 조회+++++++++++++++")
            print(type(rqid))
            print('Request Data rqid: ' + str(rqid))
            self.rqidD[rqid] = TR_Name
        except Exception as e:
            print(f"Error in RequestData: {e}")
     

    #자동 매도 신청
    def sell_stock(self):
        self.flag = "매도"
        print(self.flag)
        gaejwa_text = main_ui.textEdit.toPlainText()
        PW_text = main_ui.textEdit_2.toPlainText()

        TR_Name = "SABA101U1"      
        ret= giTop50Show.SetQueryName(TR_Name)  
        ret = giTop50Show.SetSingleData(1,"01")#계좌 상품(항상01)
        ret = giTop50Show.SetSingleData(2,"0000")#계좌 비밀번호
        ret = giTop50Show.SetSingleData(0,"27051496084")#계좌번호
        ret = giTop50Show.SetSingleData(3,"")#계좌 관리부점코드
        ret = giTop50Show.SetSingleData(4,"")#시장거래구분
        ret = giTop50Show.SetSingleData(5,"0")#선물대용매도여부
        ret = giTop50Show.SetSingleData(6,"00")#신용거래구분
        ret = giTop50Show.SetSingleData(7,"1") #매도/매수 구분
        ret = giTop50Show.SetSingleData(8,"A005930")#종목코드
        ret = giTop50Show.SetSingleData(9,"5")#주문수량
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

    # def RTOCX1_ReceiveRTData(self,giCtrl,RealType):
    #     if RealType == "AD":
    #         main_ui.tableWidget_3.insertRow(main_ui.tableWidget_3.rowCount())
    #         final_rowCount = main_ui.tableWidget_3.rowCount() - 1
    #         main_ui.tableWidget_3.setItem(final_rowCount,0,QTableWidgetItem(str(giCtrl.GetSingleData(2))))#종목코드
    #         main_ui.tableWidget_3.setItem(final_rowCount,1,QTableWidgetItem(str(giCtrl.GetSingleData(3))))#종목명
    #         main_ui.tableWidget_3.setItem(final_rowCount,2,QTableWidgetItem(str(giCtrl.GetSingleData(6))))#잔고수량
    #         main_ui.tableWidget_3.setItem(final_rowCount,3,QTableWidgetItem(str(giCtrl.GetSingleData(7))))#평균단가
    #         main_ui.tableWidget_3.setItem(final_rowCount,4,QTableWidgetItem(str(giCtrl.GetSingleData(17))))#현재가
    #         main_ui.tableWidget_3.setItem(final_rowCount,5,QTableWidgetItem(str(giCtrl.GetSingleData(13))))#손익률

    def RTOCX1_ReceiveRTData(self, giCtrl, RealType):
        if RealType == "AA":
            print("AA")
            main_ui.tableWidget_3.insertRow(main_ui.tableWidget_3.rowCount())
            final_rowCount = main_ui.tableWidget_3.rowCount() - 1
            jongmok_code = str(giCtrl.GetSingleData(2))
            jongmok_name = str(giCtrl.GetSingleData(3))
            jango_suryang = int(giCtrl.GetSingleData(6))
            avg_price = float(giCtrl.GetSingleData(7))
            now_price = float(giCtrl.GetSingleData(17))
            profit = float(giCtrl.GetSingleData(13))

            print(giCtrl.GetSingleData(2))

            main_ui.tableWidget_3.setItem(final_rowCount, 0, QTableWidgetItem(jongmok_code))  # 종목코드
            main_ui.tableWidget_3.setItem(final_rowCount, 1, QTableWidgetItem(jongmok_name))  # 종목명
            main_ui.tableWidget_3.setItem(final_rowCount, 2, QTableWidgetItem(str(jango_suryang)))  # 잔고수량
            main_ui.tableWidget_3.setItem(final_rowCount, 3, QTableWidgetItem(str(avg_price)))  # 평균단가
            main_ui.tableWidget_3.setItem(final_rowCount, 4, QTableWidgetItem(str(now_price)))  # 현재가
            main_ui.tableWidget_3.setItem(final_rowCount, 5, QTableWidgetItem(str(profit)))  # 손익률


        elif RealType == "AD":
            print(giCtrl.GetSingleData(6))

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
        #체결 조회
        elif TR_Name == "SABA231Q1":
            nCnt = giCtrl.GetMultiRowCount()
            current_chegyeol_data = []
            print("++++++++++++++++++++++++++++++++")
            print(nCnt)

            
            for i in range(nCnt):
                current_chegyeol_data.append([
                   str(giCtrl.GetMultiData(i, 0)),
                   str(giCtrl.GetMultiData(i, 14)),
                   str(giCtrl.GetMultiData(i, 15)),
                   str(giCtrl.GetMultiData(i, 30)),
                   str(giCtrl.GetMultiData(i, 24)),
                   str(giCtrl.GetMultiData(i, 25)),
                   str(giCtrl.GetMultiData(i, 26)),
                ])
                main_ui.tableWidget_2.setItem(i,0,QTableWidgetItem(str(giCtrl.GetMultiData(i, 0)))) #주문번호
                main_ui.tableWidget_2.setItem(i,1,QTableWidgetItem(str(giCtrl.GetMultiData(i, 14))))#종목명
                main_ui.tableWidget_2.setItem(i,2,QTableWidgetItem(str(giCtrl.GetMultiData(i, 15))))#주문수량
                main_ui.tableWidget_2.setItem(i,3,QTableWidgetItem(str(giCtrl.GetMultiData(i, 30))))#주문단가
                main_ui.tableWidget_2.setItem(i,4,QTableWidgetItem(str(giCtrl.GetMultiData(i, 24))))#체결수량
                main_ui.tableWidget_2.setItem(i,5,QTableWidgetItem(str(giCtrl.GetMultiData(i, 25))))#체결단가
                main_ui.tableWidget_2.setItem(i,6,QTableWidgetItem(str(giCtrl.GetMultiData(i, 26))))#미체결수량
               
                 
            # 이전에 조회한 데이터와 현재 조회한 데이터 비교
             # 이전에 조회한 데이터와 현재 조회한 데이터 비교
            differences = [i for i, (prev, current) in enumerate(zip(self.previous_chegyeol_data, current_chegyeol_data), start=1) if prev != current]
            if differences:
                print("새로운 체결 내역이 있습니다. 차이가 있는 항목:")
                try:
                    raw_time = giCtrl.GetMultiData(differences[0], 22)
                    structured_time = time.strptime(raw_time, "%H%M%S")
                    formatted_time = time.strftime("%H:%M:%S", structured_time)
                    send_message = formatted_time + "분에 " + str(giCtrl.GetMultiData(differences[0], 0)) + str(giCtrl.GetMultiData(differences[0],4 ))+ "개 체결됐습니다."
                    print(send_message)
                    bot.sendMessage(id,send_message)
                except :
                    print("매수")
                

            self.previous_chegyeol_data = current_chegyeol_data   
            

                
        #매수
        elif TR_Name == "SABA101U1" :
            if self.flag == "매수":
                try:
                    print("===========매수 response==============")
                    buy_text = '\n'.join(giCtrl.GetSingleData(0))
                    buy_text = "주문 번호 : " + str(giCtrl.GetSingleData(0) +"\n")
                    buy_text += giCtrl.GetSingleData(3) +"\n"+ giCtrl.GetSingleData(4)
                    #매수 팝업
                    QMessageBox.information(self,'매수 주문',buy_text)
                    #매수 텔레그렘 메세지
                    bot.sendMessage(id,buy_text)
                except Exception as e:
                    print(e)
            else :
                try:
                    print("===========매도 response==============")
                    sell_text = '\n'.join(giCtrl.GetSingleData(0))
                    sell_text = "주문 번호 : " + str(giCtrl.GetSingleData(0) +"\n")
                    sell_text += giCtrl.GetSingleData(3) +"\n"+ giCtrl.GetSingleData(4)+ "\n"+ giCtrl.GetSingleData(5)
                    #매수 팝업
                    QMessageBox.information(self,'매도 주문',sell_text)
                    #매수 텔레그렘 메세지
                    bot.sendMessage(id,sell_text)
                except Exception as e:
                    print(e)


        elif TR_Name == "SABA609Q1":
            try: 
                print("===========잔고 response==============")
                count = giCtrl.GetMultiRowCount()
                for i in range(count):
                    print(giCtrl.GetMultiData(i,0))
                    print(giCtrl.GetMultiData(i,20))
                #매수 팝업
                # QMessageBox.information(self,'매수 주문',buy_text)
                # #매수 텔레그렘 메세지
                # bot.sendMessage(id,buy_text)
            except Exception as e:
                print(e)


                    

                       
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    IndiWindow = indiWindow()    
    IndiWindow.show()
    app.exec_()
    
