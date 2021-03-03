import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import datetime


def get_kospi200_list():
    """'https://finance.naver.com/'에서 kospi200의 종목코드와 종목명을 스크래핑합니다.
    Returns: kospi200의 종목코드와 종목명 dataframe
    """
    stock_list = []
    base_url = "https://finance.naver.com/sise/entryJongmok.nhn?&page="

    for i in range(1, 21):
        try:
            url = base_url + str(i)
            r = requests.get(url)
            soup = BeautifulSoup(r.text, "lxml")
            items = soup.find_all("td", {"class": "ctg"})

            for item in items:
                txt = item.a.get("href")
                k = re.search("[\d]+", txt)

                if k:
                    code = k.group()
                    name = item.text
                    data = code, name
                    stock_list.append(data)
        except:
            pass

        finally:
            kospi200 = pd.DataFrame(stock_list, columns=["종목코드", "종목명"])

    return kospi200


def get_kosdak150_list():
    """'https://finance.naver.com/'에서 kosdak150의 종목코드와 종목명을 스크래핑합니다.
    Returns: kospi200의 종목코드와 종목명 dataframe
    """
    stock_lst = []
    base_url = "https://finance.naver.com/sise/sise_market_sum.nhn?sosok=1&page="

    for i in range(1, 4):
        url = base_url + str(i)
        r = requests.get(url)
        soup = BeautifulSoup(r.text, "lxml")
        items = soup.find("table", {"class": "type_2"}).find_all("a")

        for j in range(1, 51):
            txt = items[2 * j - 2].get("href")
            k = re.search("[\d]+", txt)
            if k:
                code = k.group()
                name = items[2 * j - 2].text
                data = code, name
                stock_lst.append(data)
            else:
                pass
        kosdak150 = pd.DataFrame(stock_lst, columns=["종목코드", "종목명"])

    return kosdak150


def get_history(itemcode, years):
    """과거 주가 데이터를 스크래핑합니다.
    Args:
        itemcode: 종목코드
        years: 스크래핑할 기간
    Returns: Dataframe을 반환합니다.
    """
    # 현재 날짜 가져오기
    today = datetime.datetime.now()
    duration = float(years) * 365
    # 365일 = 248 (1년 기준)
    real_duration = float(duration) / 1.47

    url = f"https://fchart.stock.naver.com/sise.nhn?symbol={itemcode}&timeframe=day&count={real_duration}&requestType=0"
    result = requests.get(url)
    bs_obj = BeautifulSoup(result.content, "html.parser")
    price_data = bs_obj.select("item")

    data_dict = {}
    date_list = []
    start_price_list = []
    high_price_list = []
    low_price_list = []
    close_price_list = []
    amount_list = []

    for i in range(len(price_data)):
        temp = str(price_data[i])[12:-9]
        temp_list = temp.split("|")

        date = temp_list[0]
        start_price = float(temp_list[1])
        high_price = float(temp_list[2])
        low_price = float(temp_list[3])
        close_price = float(temp_list[4])
        amount = float(temp_list[5])

        date_list.append(date)
        start_price_list.append(start_price)
        high_price_list.append(high_price)
        low_price_list.append(low_price)
        close_price_list.append(close_price)
        amount_list.append(amount)

    data_dict["start price"] = start_price_list
    data_dict["high price"] = high_price_list
    data_dict["low price"] = low_price_list
    data_dict["close price"] = close_price_list
    data_dict["amount"] = amount_list
    stock_data = pd.DataFrame(data_dict, index=date_list)

    return stock_data