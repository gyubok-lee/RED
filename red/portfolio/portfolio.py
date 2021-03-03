import os
import pandas as pd
import ast
from datetime import datetime


class Portfolio:
    def __init__(self, path=os.getcwd()):
        self.user_path = path + "/data/users/userDB.csv"
        self.data_path = path + "/data"
        self.latest_date = datetime.today()
        if not os.path.isfile(self.user_path):
            print('"userDB.csv"이 없습니다.')
            return

    def calculate_return(self):
        userDB = pd.read_csv(self.user_path, encoding="cp949", index_col=0)

        for index, user in userDB.iterrows():
            buy_price_lst = []
            sell_price_lst = []
            self.stock_return(user, buy_price_lst, sell_price_lst)
            self.etf_return(user, buy_price_lst, sell_price_lst)
            self.bond_return(user, buy_price_lst, sell_price_lst)
            current_return = (sum(sell_price_lst) / sum(buy_price_lst) * 100 - 100).round(2)
            userDB.loc[index, "현재 수익률(%)"] = current_return
            userDB.loc[index, "수익률 기준 날짜"] = self.latest_date
        userDB.to_csv(self.user_path, encoding="cp949")

    def stock_return(self, user, buy_price_lst, sell_price_lst):
        stock_lst = ast.literal_eval(user.주식)
        if len(stock_lst) == 0:
            return
        for i in range(len(stock_lst)):
            stock_name = stock_lst[i][0]
            latest_price = self.get_latest_price("stock", stock_name)
            sell_price = latest_price * stock_lst[i][1][0]
            buy_price = stock_lst[i][1][1][0] * stock_lst[i][1][0]
            sell_price_lst.append(sell_price)
            buy_price_lst.append(buy_price)

    def etf_return(self, user, buy_price_lst, sell_price_lst):
        etf_lst = ast.literal_eval(user.ETF)
        if len(etf_lst) == 0:
            return
        for i in range(len(etf_lst)):
            etf_name = etf_lst[i][0]
            latest_price = self.get_latest_price("etf", etf_name)
            sell_price = latest_price * etf_lst[i][1][0]
            buy_price = etf_lst[i][1][1][0] * etf_lst[i][1][0]
            sell_price_lst.append(sell_price)
            buy_price_lst.append(buy_price)

    def bond_return(self, user, buy_price_lst, sell_price_lst):
        bond_lst = ast.literal_eval(user.채권)
        if len(bond_lst) == 0:
            return
        for i in range(len(bond_lst)):
            bond_name = bond_lst[i][0]
            latest_price = self.get_latest_price("etf", bond_name)
            sell_price = latest_price * bond_lst[i][1][0]
            buy_price = bond_lst[i][1][1][0] * bond_lst[i][1][0]
            sell_price_lst.append(sell_price)
            buy_price_lst.append(buy_price)

    def get_latest_price(self, category, name):
        file_path = os.path.join(self.data_path, category, name)
        file_path = file_path + ".csv"
        df = pd.read_csv(file_path, encoding="cp949", index_col=0)
        latest_price = df.iloc[-1, :]["close price"]
        self.latest_date = df.index[-1]
        return latest_price
