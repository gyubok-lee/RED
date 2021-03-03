from . import stock
from . import etf
from . import finance
import pandas as pd
import numpy as np
import os
from tqdm import tqdm

pd.options.mode.chained_assignment = None


class Scraper:
    def __init__(self, path=os.getcwd()):
        self.path = path
        data_path = os.path.join(self.path, "data")
        if not os.path.isdir(data_path):
            os.makedirs(data_path)

    def stock_list(self):
        """kospi200, kosdak150 리스트를 스크래핑하여 저장합니다."""
        kospi_df = stock.get_kospi200_list()
        kosdak_df = stock.get_kosdak150_list()
        kospi_df["분류"] = "kospi200"
        kosdak_df["분류"] = "kosdak150"
        kospidak_df = pd.concat([kospi_df, kosdak_df], ignore_index=True)
        
        old = pd.read_csv(self.path + "/data/stock_list.csv", encoding="cp949",usecols=["분류","종목코드", "종목명"]) # 기존
        old= old[~old.종목명.isin(kospidak_df['종목명'].values)] # 새로운거에는 없는 기존꺼
        kospidak_df = pd.concat([kospidak_df,old]).drop_duplicates().reset_index(drop=True)
        
        # stock list 저장
        kospidak_df.to_csv(self.path + "/data/stock_list.csv", encoding="cp949", index=False)

    def stock_history(self, years=10, path="/data/stock"):
        """각 종목별 과거 데이터를 스크래핑 및 저장합니다.
        Args:
            years: 스크래핑할 기간(현재로부터)
            path: 주가 데이터 저장 경로(default: "/data/stock")
        """
        stock_path = self.path + path
        if not os.path.isdir(stock_path):
            os.makedirs(stock_path)
        try:
            kospidak_df = pd.read_csv(self.path + "/data/stock_list.csv", encoding="cp949")
        except FileNotFoundError:
            print('"stock_list.csv" 파일을 찾을 수 없습니다. stock_list()를 먼저 실행해주세요.')
            return

        for itemcode, itemname in tqdm(zip(kospidak_df["종목코드"], kospidak_df["종목명"])):
            itemcode = str(itemcode).zfill(6)
            stock_df = stock.get_history(itemcode, years)
            file_name = os.path.join(stock_path, "{}.csv".format(itemname))
            stock_df.to_csv(file_name, encoding="cp949")

        print("주식 데이터 스크래핑이 완료되었습니다.")

    # def update_stock():

    def etf_list(self):
        """ETF 리스트를 스크래핑하여 저장합니다."""
        etf_df = etf.get_etf_list()
        etf_df.to_csv(self.path + "/data/etf_list.csv", index=False, encoding="cp949")

    def etf_history(self, years=10, path="/data/etf"):
        """각 종목별 과거 데이터를 스크래핑 및 저장합니다.
        Args:
            years: 스크래핑할 기간(현재로부터)
            path: 주가 데이터 저장 경로(default: "/data/etf")
        """
        etf_path = self.path + path
        if not os.path.isdir(etf_path):
            os.makedirs(etf_path)

        try:
            etf_list_df = pd.read_csv(self.path + "/data/etf_list.csv", encoding="cp949")
        except FileNotFoundError:
            print('"etf_list.csv" 파일을 찾을 수 없습니다. etf_list()를 먼저 실행해주세요.')
            return

        for itemcode, itemname in tqdm(zip(etf_list_df["itemcode"], etf_list_df["itemname"])):
            itemcode = str(itemcode).zfill(6)
            etf_df = stock.get_history(itemcode, years)
            file_name = os.path.join(etf_path, "{}.csv".format(itemname))
            etf_df.to_csv(file_name, encoding="cp949")

        print("ETF 데이터 크롤링이 완료되었습니다.")

    # def update_etf():

    def finance(self, path="/data/finance"):
        """각 종목별 재무정보를 스크래핑 및 저장합니다.
        Args:
            path: 주가 데이터 저장 경로(default: "/data/finance")
        """
        finance_path = self.path + path
        if not os.path.isdir(finance_path):
            os.makedirs(finance_path)

        ROE = []
        PER = []
        kospidak_df = pd.read_csv(self.path + "/data/stock_list.csv", encoding="cp949")
        # 각 종목별 재무정보 저장 / 예상 컨센서스 데이터가 있어서, 빈 데이터 들이 많음.
        for itemcode, itemname in tqdm(zip(kospidak_df["종목코드"], kospidak_df["종목명"])):
            itemcode = str(itemcode).zfill(6)
            try: 
                finance_df = finance.get_finance(itemcode)

                temp = finance_df[["영업이익률", "PER(배)"]]
                temp["영업이익률"].replace("", np.nan, inplace=True)
                temp["PER(배)"].replace("", np.nan, inplace=True)
                temp = temp.dropna()

                ROE.append(list(temp["영업이익률"].values[-2:]))
                PER.append(list(temp["PER(배)"].values[-2:]))

                file_name = os.path.join(finance_path, "{}.csv".format(itemname))
                finance_df.to_csv(file_name, encoding="cp949")
            except :
                ROE.append(['-100','-100'])
                PER.append(['100','100'])

        kospidak_df["영업이익률"] = ROE
        kospidak_df["PER"] = PER
        
        
        kospidak_df.to_csv(self.path + "/data/stock_list.csv", encoding="cp949")
        print("재무제표 데이터 크롤링이 완료되었습니다.")

    def runAll(self):
        self.stock_list()
        self.stock_history()
        #self.etf_list() 
        self.etf_history()
        self.finance()
