import requests
import json
from pandas.io.json import json_normalize
from bs4 import BeautifulSoup
import re


def get_etf_list():
    """'https://finance.naver.com/'에서 ETF 리스트를 스크래핑합니다.
    Returns: etf list를 dataframe으로 반환합니다.
    """
    # 네이버 금융 API로부터 ETF 데이터 갖고오기
    url = "https://finance.naver.com/api/sise/etfItemList.nhn"
    json_data = json.loads(requests.get(url).text)
    df = json_normalize(json_data["result"]["etfItemList"])

    # etf 데이터프레임 정제
    # etfTabCode = {1: 국내 시장지수, 4: 해외 주식, 6: 채권}
    etf_df = df[["itemcode", "etfTabCode", "itemname"]]
    etf_df = etf_df[etf_df["etfTabCode"].isin([1, 4, 6])]

    # # 52주 베타값 0으로 초기화
    # etf_df["YR_BETA"] = 0
    # etf_df.reset_index(drop=True, inplace=True)

    # for i in etf_df.index:
    #     itemcode = etf_df.loc[i]["itemcode"]
    #     item_url = "https://finance.naver.com/item/coinfo.nhn?code={}".format(itemcode)
    #     result = requests.get(item_url)
    #     bs_obj = BeautifulSoup(result.content, "html.parser")

    #     # 52주 베타값 스크래핑
    #     iframe = bs_obj.find("iframe", {"title": "종목분석 영역"})
    #     iframe_url = requests.get(iframe.get("src"))
    #     iframe_obj = BeautifulSoup(iframe_url.content, "html.parser")
    #     script = str(iframe_obj.find_all("script", {"type": "text/javascript"})[3])
    #     pattern = re.compile('"YR_BETA":".*')
    #     YR_BETA = pattern.findall(script)
    #     YR_BETA = YR_BETA[0].split(",")[0][11:-1]
    #     etf_df.loc[i, "YR_BETA"] = YR_BETA

    etf_df["etfTabCode"].loc[etf_df["etfTabCode"] == 1] = "국내시장지수"
    etf_df["etfTabCode"].loc[etf_df["etfTabCode"] == 4] = "해외주식"
    etf_df["etfTabCode"].loc[etf_df["etfTabCode"] == 6] = "채권"
    return etf_df
