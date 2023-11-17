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
check = "체결만"
auto_sell = False

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
        main_ui.pushButton_2.clicked.connect(self.chegyeol_show_all) #체결 내역 버튼
        main_ui.pushButton_3.clicked.connect(self.show_jango) #실시간 잔고 버튼
        main_ui.pushButton_4.clicked.connect(self.handle_auto_sell) # 매도 예약 버튼
        main_ui.pushButton_5.clicked.connect(self.sell_stock) # 매도 주문 버튼
        main_ui.tableWidget.itemClicked.connect(self.on_table_item_clicked)
        main_ui.tableWidget_3.itemClicked.connect(self.on_table_item_clicked2)

        self.auto_sell = False

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

        #시작하자마자 장중 매매현황 출력
        TR_Name = "TR_INDI004"  
        ret = giTop50Show.SetQueryName(TR_Name)   
        ret = giTop50Show.SetSingleData(0,"2")
        ret = giTop50Show.SetSingleData(1,"10") #기관 순매수
        rqid = giTop50Show.RequestData()
        print(type(rqid))

        print('Request Data rqid: ' + str(rqid))
        self.rqidD[rqid] = TR_Name 

        # 주기적으로 체결 결과를 조회하는 스케쥴러 -> view_trade_history 함수를 호출하는 타이머 생성
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.chegyeol_show_one)
        self.timer.start(10000)  # 60초(60,000 밀리초)마다 타이머 이벤트 발생
        self.timer.timeout.connect(self.show_jango)
        self.timer.start(10000)  # 60초(60,000 밀리초)마다 타이머 이벤트 발생

    def on_table_item_clicked(self, item):
        # 클릭한 셀의 행(row)과 열(column) 가져오기
        row = item.row()
        col = item.column()

        # 테이블 셀의 텍스트 가져오기
        cell_text = item.text()

        if col == 0:
            # textEdit_3에 클릭한 셀의 내용 표시
            main_ui.textEdit_3.setText("A"+cell_text)

    def on_table_item_clicked2(self, item):
        # 클릭한 셀의 행(row)과 열(column) 가져오기
        row = item.row()
        col = item.column()

        # 테이블 셀의 텍스트 가져오기
        cell_text = item.text()

        if col == 0:
            # textEdit_3에 클릭한 셀의 내용 표시
            main_ui.textEdit_8.setText(cell_text)

    #매수 주문
    def buy_stock(self):
        self.flag = "매수"
        jongmok_code = main_ui.textEdit_3.toPlainText()
        jumun_suryang = main_ui.textEdit_4.toPlainText()
        # jongmok_code="A005930"
        # jumun_suryang="1"
        # price=""
        TR_Name = "SABA101U1"          
        ret= giTop50Show.SetQueryName(TR_Name)  

        if jongmok_code == "":
           QMessageBox.information(self,"필수 항목 부족" ,"종목 코드를 입력해주세요.")
           return
        if jumun_suryang == "":
           QMessageBox.information(self,"필수 항목 부족" ,"주문 수량을 입력해주세요.")
           return

        ret = giTop50Show.SetSingleData(0,"27051496084")#계좌번호
        ret = giTop50Show.SetSingleData(1,"01")#계좌 상품(항상01)
        ret = giTop50Show.SetSingleData(2,"0000")#계좌 비밀번호
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
    
    #체결 내역 조회(체결 미체결 모두)
    def chegyeol_show_all(self):
        self.check = "모두"
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
            print(type(rqid))
            print('Request Data rqid: ' + str(rqid))
            self.rqidD[rqid] = TR_Name
        except Exception as e:
            print(f"Error in RequestData: {e}")

     #체결 내역 조회(체결만)
    def chegyeol_show_one(self):
        self.check = "체결만"
        TR_Name = "SABA231Q1"             
        ret = giTop50Show.SetQueryName(TR_Name)
        # gaejwa_text = main_ui.textEdit.toPlainText()
        # PW_text = main_ui.textEdit_2.toPlainText()

        ret = giTop50Show.SetSingleData(0,self.get_date()) #매매일자
        ret = giTop50Show.SetSingleData(1,"27051496084") #계좌번호
        ret = giTop50Show.SetSingleData(2,"0000") #비밀번호
        ret = giTop50Show.SetSingleData(3,"00") #장구분
        ret = giTop50Show.SetSingleData(4,"1") #체결구분- 체결만
        ret = giTop50Show.SetSingleData(5,"1") #건별구분
        ret = giTop50Show.SetSingleData(6,"*") #입력종목코드
        ret = giTop50Show.SetSingleData(7,"") #계계좌상품코드
        ret = giTop50Show.SetSingleData(8,"Y") #작업구분
        try:
            rqid = giTop50Show.RequestData()
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

    #잔고 조회
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

    #매도 신청
    def sell_stock(self):
        self.flag = "매도"
        jongmok_code = main_ui.textEdit_8.toPlainText()
        jumun_suryang = main_ui.textEdit_9.toPlainText()

        if jongmok_code == "":
           QMessageBox.information(self,"필수 항목 부족" ,"종목 코드를 입력해주세요.")
           return
        if jumun_suryang == "":
           QMessageBox.information(self,"필수 항목 부족" ,"주문 수량을 입력해주세요.")
           return

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

    def handle_auto_sell(self):
        self.auto_sell = True
        jongmok_code = main_ui.textEdit_10.toPlainText()
        jumun_suryang = main_ui.textEdit_11.toPlainText()
        plus = main_ui.textEdit_7.toPlainText()
        minus = main_ui.textEdit_6.toPlainText()

        if jongmok_code == "":
          QMessageBox.information(self,"필수 항목 부족" ,"종목명을 입력해주세요.")
          return
        if jumun_suryang == "":
          QMessageBox.information(self,"필수 항목 부족" ,"주문 수량을 입력해주세요.")
          return
        if plus == "":
          QMessageBox.information(self,"필수 항목 부족" ,"이익 수익률을 입력해주세요.")
          return
        if minus == "":
          QMessageBox.information(self,"필수 항목 부족" ,"손실 제한률을 입력해주세요.")
          return
         #매도 팝업
        QMessageBox.information(self,"매도예약" ,jongmok_code+" 매도 예약이 신청되었습니다.")
        #매도 텔레그렘 메세지
        bot.sendMessage(id,jongmok_code + " 매도 예약이 신청되었습니다. ")
    #예약 매도 신청
    def sell_stock_auto(self):
        self.flag = "매도"
        self.auto_sell == False
        jongmok_code = main_ui.textEdit_10.toPlainText()
        jumun_suryang = main_ui.textEdit_11.toPlainText()

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

        if TR_Name == "TR_INDI004":
            nCnt = giCtrl.GetMultiRowCount()
            for i in range(0, nCnt):
                tr_data_output.append([])
                main_ui.tableWidget.setItem(i,0,QTableWidgetItem(str(giCtrl.GetMultiData(i, 0))))#단축코드
                main_ui.tableWidget.setItem(i,1,QTableWidgetItem(str(giCtrl.GetMultiData(i, 1))))#종목명
                main_ui.tableWidget.setItem(i,2,QTableWidgetItem(str(giCtrl.GetMultiData(i, 2))))#현재가
                main_ui.tableWidget.setItem(i,3,QTableWidgetItem(str(giCtrl.GetMultiData(i, 4))))#전일대비
                main_ui.tableWidget.setItem(i,4,QTableWidgetItem(str(giCtrl.GetMultiData(i, 5))))#누적거래량
                main_ui.tableWidget.setItem(i,5,QTableWidgetItem(str(giCtrl.GetMultiData(i, 30))))#기관계매수
                main_ui.tableWidget.setItem(i,6,QTableWidgetItem(str(giCtrl.GetMultiData(i, 31))))#기관계매도
                main_ui.tableWidget.setItem(i,7,QTableWidgetItem(str(giCtrl.GetMultiData(i, 32))))#기관계순매수
                for j in range(0,9):
                    tr_data_output[i].append(giCtrl.GetMultiData(i, j))
                    
            print(type(tr_data_output))
        #체결 조회
        elif TR_Name == "SABA231Q1":
            nCnt = giCtrl.GetMultiRowCount()
            if self.check == "체결만":
                current_chegyeol_data = []
                print("++++++++++++++체결만+++++++++++++++++")
                
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
                    
                # 이전에 조회한 데이터와 현재 조회한 데이터 비교
                differences = [i for i, (prev, current) in enumerate(zip(self.previous_chegyeol_data, current_chegyeol_data), start=1) if prev != current]
                if differences:
                    print("새로운 체결 내역이 있습니다")
                    try:
                        raw_time = giCtrl.GetMultiData(differences[0]-1, 22)
                        structured_time = time.strptime(raw_time, "%H%M%S")
                        formatted_time = time.strftime("%H:%M:%S", structured_time)
                        send_message = formatted_time + "분에 " + str(giCtrl.GetMultiData(differences[0]-1, 0)) +"가 체결됐습니다."
                        print(send_message)
                        bot.sendMessage(id,send_message)
                    except :
                        print("error")
                self.previous_chegyeol_data = current_chegyeol_data   
            else:
                print("++++++++++++++체결미체결+++++++++++++++++")

                for i in range(nCnt):
                    sell_buy = "매수"
                    if giCtrl.GetMultiData(i, 4) == "1":
                      sell_buy = "매도"
                    
                    main_ui.tableWidget_2.setItem(i,0,QTableWidgetItem(str(giCtrl.GetMultiData(i, 0)))) #주문번호
                    main_ui.tableWidget_2.setItem(i,1,QTableWidgetItem(str(giCtrl.GetMultiData(i, 14))))#종목명
                    main_ui.tableWidget_2.setItem(i,2,QTableWidgetItem(str(giCtrl.GetMultiData(i, 15))))#주문수량
                    main_ui.tableWidget_2.setItem(i,3,QTableWidgetItem(sell_buy))#매수매도 구분
                    main_ui.tableWidget_2.setItem(i,4,QTableWidgetItem(str(giCtrl.GetMultiData(i, 24))))#체결수량
                    main_ui.tableWidget_2.setItem(i,5,QTableWidgetItem(str(giCtrl.GetMultiData(i, 25))))#체결단가
                    main_ui.tableWidget_2.setItem(i,6,QTableWidgetItem(str(giCtrl.GetMultiData(i, 26))))#미체결수량



        #잔고 조회 
        elif TR_Name == "SABA609Q1":
            nCnt = giCtrl.GetMultiRowCount()
            print("+++++++++잔고조회+++++++++++")
            plus = main_ui.textEdit_7.toPlainText()
            minus = main_ui.textEdit_6.toPlainText()
            
            jongmok_code = main_ui.textEdit_10.toPlainText()
            print(plus,minus)
            for i in range(0, nCnt):
                #예약 매도를 했다면
                #print(self.auto_sell)
                if self.auto_sell:
                    if(str(giCtrl.GetMultiData(i, 0))==jongmok_code and( float(giCtrl.GetMultiData(i, 20))>=float(plus) or float(giCtrl.GetMultiData(i, 20))<=float(minus))):
                        self.auto_sell =False
                        self.sell_stock_auto()
                
                main_ui.tableWidget_3.setItem(i,0,QTableWidgetItem(str(giCtrl.GetMultiData(i, 0)))) #종목코드
                main_ui.tableWidget_3.setItem(i,1,QTableWidgetItem(str(giCtrl.GetMultiData(i, 1)))) #종목명
                main_ui.tableWidget_3.setItem(i,2,QTableWidgetItem(str(giCtrl.GetMultiData(i, 4)))) #잔고수량
                main_ui.tableWidget_3.setItem(i,3,QTableWidgetItem(str(giCtrl.GetMultiData(i, 12)))) #평균단가
                main_ui.tableWidget_3.setItem(i,4,QTableWidgetItem(str(giCtrl.GetMultiData(i, 13)))) #현재가
                main_ui.tableWidget_3.setItem(i,5,QTableWidgetItem(str(giCtrl.GetMultiData(i, 20)))) #손익률

        #매수 & 매도
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
                    QMessageBox.information(self,'매수 불가',"매수 주문 실패")
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
                    QMessageBox.information(self,'매도 불가',"매도 주문 실패")
                  
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    IndiWindow = indiWindow()    
    IndiWindow.show()
    app.exec_()
    
    
