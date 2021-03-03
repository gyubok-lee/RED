from . import stock
from . import etf
import os
import pandas as pd
import ast

class Recommender:
    def __init__(self, path, stock_path, etf_path, sector):
        self.path = path
        self.stock_path = stock_path
        self.etf_path = etf_path
        self.sector = sector

    def rec_stock(self):
        recommend_lst = []
        print("추천 주식 종목 찾는 중...")
        for i in os.listdir(self.stock_path):
            stock_data = pd.read_csv(self.stock_path + "/" + i, encoding="cp949")
            stock_name = i[:-4]
            stock.gold_cross(stock_name, stock_data, recommend_lst)
            stock.r_sigma(stock_name, stock_data, recommend_lst)
            stock.long_candle(stock_name, stock_data, recommend_lst)
            stock.mfi_checker(stock_name, stock_data, recommend_lst)
            stock.rsi_sto_cross(stock_name, stock_data, recommend_lst)
            stock.amount_attention(stock_name, stock_data, recommend_lst)
            stock.bollinger(stock_name, stock_data, recommend_lst)
        return recommend_lst

    def rec_etf(self):
        lst1 = []  # 채권 etf
        lst2 = []  # 그외 etf
        print("추천 ETF 찾는 중...")
        etfs = pd.read_csv(self.path + "/data/etf_list.csv", encoding="cp949")
        bonds = etfs[etfs["etfTabCode"] == "채권"]["itemname"].values
        sector_etfs = etfs[etfs["섹터"] == self.sector]["itemname"].values

        for i in os.listdir(self.etf_path):
            etf_data = pd.read_csv(self.etf_path + "/" + i, encoding="cp949")
            etf.momentum(i, etf_data, lst1, lst2, bonds)

        lst1.sort(key=lambda x: x[1])
        lst2.sort(key=lambda x: x[1])
        lst1.sort(key=lambda x: x[2], reverse=True)
        lst2.sort(key=lambda x: x[2], reverse=True)
        
        for y in lst2:
            if y[0] in sector_etfs:
                lst2.remove(y)
                lst2.insert(0, y) #맨 앞으로 이동 최우선 추출
                break
        
        return lst1[:20], lst2[:20]
    
    def cal_weight(self):
        self.df = pd.read_csv(self.path + "/data/stock_list.csv", index_col = 0, encoding = 'cp949')
        for i in range(len(self.df)):
            if self.df.영업이익률[i] == '[]':
                self.df.영업이익률[i] = "['1','1']"
            if self.df.PER[i] == '[]':
                self.df.PER[i] = "['-1','-1']"
        self.가중치 = []
        self.df.영업이익률 = self.df.영업이익률.apply(ast.literal_eval)
        self.df.PER = self.df.PER.apply(ast.literal_eval)
        for i in range(len(self.df)):
            영업이익률1, 영업이익률2 = float(self.df.영업이익률[i][0].replace(",","")), float(self.df.영업이익률[i][-1].replace(",",""))
            PER1, PER2 = float(self.df.PER[i][0].replace(",","")), float(self.df.PER[i][-1].replace(",",""))
            
            self.df.PER[i] = (PER1 + PER2) /2
            self.df.영업이익률[i] = (영업이익률1 + 영업이익률2) / 2
            
            self.a = self.df.영업이익률[i]/100 + 1/(self.df.PER[i])
            self.가중치.append(self.a)
        self.df['가중치'] = self.가중치

        self.df.to_csv(self.path + "/data/stock_list2.csv", encoding = 'cp949')
        return self.df