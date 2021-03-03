import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup


def get_finance(itemcode):
    """각 종목별 재무정보를 스크래핑 합니다.
    Args:
        itemcode: 종목코드
    Returns: Dataframe을 반환합니다.
    """
    URL = "https://finance.naver.com/item/main.nhn?code=" + itemcode
    stock_info = requests.get(URL)
    html = stock_info.text
    soup = BeautifulSoup(html, "html.parser")

    finance_html = soup.select("div.section.cop_analysis div.sub_section")[0]

    th_data = [item.get_text().strip() for item in finance_html.select("thead th")]
    annual_date = th_data[3:7]  # 연 데이터
    quarter_date = th_data[7:13]  # 분기 데이터

    finance_index = [
        item.get_text().strip() for item in finance_html.select("th.h_th2")
    ][3:]
    finance_data = [item.get_text().strip() for item in finance_html.select("td")]
    finance_data = np.array(finance_data)
    finance_data.resize(len(finance_index), 10)
    finance_date = annual_date + quarter_date
    
    finance = pd.DataFrame(
        data= finance_data, index=finance_index, columns=finance_date
    )
    return finance.T  # 날짜 데이터를 가로로, 항목들을 세로로 두기 위해 설정