import pandas as pd
import numpy as np
import os
from datetime import date
import time
from tqdm import tqdm

import matplotlib.font_manager as fm
import matplotlib.pylab as plt
import matplotlib

import ipywidgets as widgets
from ipywidgets import interact
from PIL import Image, ImageFont, ImageDraw
from IPython.display import clear_output
from IPython.display import Image as disImage
from IPython.display import display

from .scraper import Scraper
from .indicator import Indicator
from .recommender import Recommender

class RED:
    def __init__(self):
        self.path = os.getcwd()
        self.stock_path = os.path.join(self.path, "data/stock")
        self.etf_path = os.path.join(self.path, "data/etf")
        self.users_path = os.path.join(self.path, "data/users")
        if not os.path.isdir(self.stock_path):
            os.makedirs(self.stock_path)
        if not os.path.isdir(self.etf_path):
            os.makedirs(self.etf_path)
        if not os.path.isdir(self.users_path):
            os.makedirs(self.users_path)

        try:
            self.total_info = pd.read_csv(
                self.path + "/data/users/userDB.csv", encoding="cp949", index_col=0
            )
        except FileNotFoundError:
            print('"userDB.csv" 파일을 찾을 수 없습니다. 먼저 userDB를 생성하겠습니다.')
            df = pd.DataFrame(
                columns=(
                    "투자 금액(만 원)",
                    "투자 기간",
                    "나이",
                    "성별",
                    "월 정기 수입(만 원)",
                    "관심산업분야",
                    "금융지식수준",
                    "위험추구성향",
                    "주식",
                    "채권",
                    "ETF",
                    "날짜",
                )
            )
            df.to_csv(self.path + "/data/users/userDB.csv", encoding="cp949")
            self.total_info = pd.read_csv(
                self.path + "/data/users/userDB.csv", encoding="cp949", index_col=0
            )

        self.stock_data = os.listdir(self.path + "/data/stock")
        self.etf_data = os.listdir(self.path + "/data/etf")
        self.start = widgets.Button(description="투자 시작")
        self.to_home_button = widgets.Button(description="뒤로 가기")
        self.crawl_setting = widgets.Button(description="데이터 업데이트")
        self.save = widgets.Button(description="결과 저장")
        self.fontpath = self.path + "/red/interface/font/NanumSquareB.ttf"

    def RED_start(self, change):
        """ "투자 시작" 클릭시 다른 모든 함수들이 실행될 주요함수"""
        self.user_info = [
            RED.capital.value,
            RED.term_dropdown.value,
            RED.age.value,
            RED.gender_dropdown.value,
            RED.income.value,
            RED.sector.value,
            RED.know.value,
            RED.risk.value,
        ]
        clear_output()

        print("입력이 완료되었습니다, 투자자 성향을 판단중입니다")
        print("···")
        time.sleep(1.5)

        self.disposition_viz()
        # 성향을 보고 자본배분 비율 선정
        # 각각 추천 -> 주식: 기간, 알고리즘 고려 / etf: 기간, 수익률, 관심분야 고려
        self.portfolios = self.mk_portfolio()
        # 추천 결과 출력 후 DB 만들고 저장.
        display(self.save)
        self.save.on_click(self.save_info)

    def save_info(self, portfolios):
        df = pd.DataFrame(
            np.array(self.user_info).reshape(1, 8),
            columns=[
                "투자 금액(만 원)",
                "투자 기간",
                "나이",
                "성별",
                "월 정기 수입(만 원)",
                "관심산업분야",
                "금융지식수준",
                "위험추구성향",
            ],
        )

        df["주식"] = [list(self.portfolios[0].items())]
        df["채권"] = [list(self.portfolios[1].items())]
        df["ETF"] = [list(self.portfolios[2].items())]
        df["날짜"] = date.today()
        df = pd.concat([self.total_info, df], ignore_index=True)
        df.to_csv(self.path + "/data/users/userDB.csv", encoding="cp949")
        print("저장되었습니다.")

    def mk_portfolio(self):
        """포트폴리오 만드는 함수, r1: ETF비율, r2 : 채권 비율"""
        capital = self.user_info[0] * 10000
        if self.user_info[7] == self.risk_list[0]:
            r1 = 1
            r2 = 0.67
        elif self.user_info[7] == self.risk_list[1]:
            r1 = 0.8
            r2 = 0.4
        elif self.user_info[7] == self.risk_list[2]:
            r1 = 0.6
            r2 = 0.3
        elif self.user_info[7] == self.risk_list[3]:
            r1 = 0.4
            r2 = 0.1
        elif self.user_info[7] == self.risk_list[4]:
            r1 = 0.2
            r2 = 0

        if self.user_info[1] == self.term_list[0] or self.user_info[1] == self.term_list[1]:
            r2 = 0  # 투자 기간이 짧으면 채권 제외

        real_r0 = int((1 - r1) * 100)
        real_r1 = int((r1 - r2) * 100)
        real_r2 = int(r2 * 100)

        recommender = Recommender(self.path, self.stock_path, self.etf_path, self.user_info[5])
        
        recommender.cal_weight()
        rec_stock_lst = recommender.rec_stock()
        
        df = pd.read_csv(self.path + "/data/stock_list2.csv", encoding = 'cp949')
        names = [i[0] for i in rec_stock_lst]
        a = list(df[df['종목명'].isin(names)][['종목명','가중치']].sort_values(by="가중치",ascending = False).종목명.values)
        rec_stock_lst.sort(key=lambda x: a.index(x[0]))
        self.rec_stocks = rec_stock_lst
        #print(rec_stock_lst)
        
        # 중복의 경우 처리필요
        
        res_etf1, res_etf2 = recommender.rec_etf()
        print("\n\n고객님의 포트폴리오입니다.\n")
        
        주식리스트 = []
        채권리스트 = []
        일반리스트 = []

        주식별금액리스트 = []
        채권별금액리스트 = []
        일반별금액리스트 = []

        self.portfolios1, penny1 = self.dist(capital, rec_stock_lst, 1 - (r1), 10)
        print("\n주식 종목 : {}원\n".format(capital * (1 - r1) - penny1))
        for name, info in self.portfolios1.items():
            print("{}, {}개 매입. {} 전략. 현재가: {}".format(name, info[0], info[1][1], info[1][0]))
            주식리스트.append(name)
            주식별금액리스트.append(info[1])

        self.portfolios2, penny2 = self.dist(capital + penny1, res_etf1, r2, 5)
        print("\n채권 ETF 종목 : {}원\n".format((capital + penny1) * r2 - penny2))
        for name, info in self.portfolios2.items():
            print("{}, {}개 매입.기간 내 보유 권장. 현재가: {}".format(name, info[0], info[1][0]))
            채권리스트.append(name)
            채권별금액리스트.append(info[1])

        self.portfolios3, penny3 = self.dist(capital + penny2, res_etf2, r1 - r2, 5)
        print("\n일반 ETF 종목 : {}원\n".format((capital + penny2) * (r1 - r2) - penny3))
        for name, info in self.portfolios3.items():
            print("{}, {}개 매입. 20일 후 리밸런싱 권장. 현재가: {}".format(name, info[0], info[1][0]))
            일반리스트.append(name)
            채권별금액리스트.append(info[1])
            
        # 포트폴리오 1번 보여주기
        self.portfolio_viz()

        ## 포트폴리오 상세정보
        주식금액 = (capital * (1 - r1) - penny1)//10000
        채권금액 = ((capital + penny1) * r2 - penny2)//10000
        일반금액 = ((capital + penny2) * (r1 - r2) - penny3)//10000

        # 막대 그래프 생성
        kindx = ["주식", "일반 ETF", "채권 ETF"]
        values = [주식금액, 일반금액, 채권금액]
        colors = ["silver", "gold", "lightgray"]

        fm.get_fontconfig_fonts()
        font_name = fm.FontProperties(fname=self.fontpath).get_name()
        plt.rc("font", family= font_name, size=20)
        

        fig = plt.figure(figsize=(7, 7))
        plt.bar(kindx, values, width=0.6, color=colors, edgecolor="lightgray")
        plt.xlabel('(만 원)')

        plt.savefig(self.path + "/red/interface/image/portfolio/bar_chart.png")
        plt.close()

        # 경로별 이미지 불러오기
        im_tend = Image.open(self.path + "/red/interface/image/portfolio/red_3.png")
        im_chart = Image.open(self.path + "/red/interface/image/portfolio/bar_chart.png")
        font = ImageFont.truetype(self.fontpath, 24)

        # 칼라 설정
        b, g, r, a = 0, 0, 0, 0

        # 이미지에 텍스트 삽입
        포트폴리오 = 주식리스트 + 채권리스트 + 일반리스트
        draw = ImageDraw.Draw(im_tend)
        try:
            draw.text((635, 120), str(포트폴리오[0]), font=font, fill=(b, g, r, a))
            draw.text((635, 164.333), str(포트폴리오[1]), font=font, fill=(b, g, r, a))
            draw.text((635, 208.666), str(포트폴리오[2]), font=font, fill=(b, g, r, a))
            draw.text((635, 253), str(포트폴리오[3]), font=font, fill=(b, g, r, a))
            draw.text((635, 297.333), str(포트폴리오[4]), font=font, fill=(b, g, r, a))
            draw.text((635, 341.666), str(포트폴리오[5]), font=font, fill=(b, g, r, a))
            draw.text((635, 386), str(포트폴리오[6]), font=font, fill=(b, g, r, a))
            draw.text((805, 430.333), "···", font=font, fill=(b, g, r, a))
        except :
            pass
          
 
        # 이미지에 파이차트 삽입
        im_tend.paste(im_chart, (30, 10))

        display(im_tend)

        # 마무리
        #portfolios4 = dict(portfolios1, **portfolios2)
        #portfolios4.update(portfolios3)
        return self.portfolios1,self.portfolios2,self.portfolios3

    def dist(self, capital, asset, pro, max_num):
        """자본 배분 알고리즘 (자본, 리스트, 비율, 최대종류)"""
        limit = capital * pro  # 최대 금액
        amount = 0  # 금액
        res = dict()  # 포트폴리오
        ofN = limit / max_num

        while True:
            more = False  # 더 넣을 값이 있는가?
            for i in range(len(asset)):
                if len(res) >= max_num and asset[i][0] not in res:  # 최대 종류 수까지 담았다면
                    break
                if limit >= amount + asset[i][1]:  # 최대금액 미만이라면
                    amount += asset[i][1]
                    res.setdefault(asset[i][0], [0, asset[i][1:]])
                    res[asset[i][0]][0] += 1
                    cnt = 1
                    while  (asset[i][1] * (cnt+1) <= ofN) & (limit >= amount + asset[i][1]) : # 균등하게 금액을 채우기
                        amount += asset[i][1]
                        res[asset[i][0]][0] += 1
                        cnt += 1
                    more = True

            # 더 못 넣는다면
            if more == False:
                break
        # print("배분가능 금액 : ",limit,"실제 배분금액 : ", amount)
        return res, limit - amount

    def data_setting(self, change):  # 실시간 종목추천을 위한 최근 데이터 크롤링 및 전처리
        print("실시간 주가 데이터를 불러오는 중입니다... (약 5분~8분 소요)")
        self.crawling_start()
        print("데이터를 처리합니다.")
        time.sleep(1)
        self.preprocess_start()

    def clear_all(self, change):
        clear_output()  # "뒤로 가기" 클릭시 인터페이스 종료

    def run(self):  # 인터페이스 및 프로그램 실행

        for i in self.user_buttons:
            display(i)

        display(self.crawl_setting)
        display(self.start)
        display(self.to_home_button)
        print("데이터 업데이트를 하신 후, 입력하신 정보를 확인하시고 투자 시작을 눌러주세요.")
        self.start.on_click(self.RED_start)
        self.to_home_button.on_click(self.clear_all)
        self.crawl_setting.on_click(self.data_setting)

    def crawling_start(self):
        scraper = Scraper()
        scraper.runAll()

    def preprocess_start(self):
        for i in tqdm(os.listdir(self.path + "/data/stock")):
            data_dir = self.path + "/data/stock/" + i
            stock_df = pd.read_csv(data_dir, index_col=0, encoding="cp949")
            stock_preprocess = Indicator(stock_df)
            stock_preprocess.runAll()
            stock_df.to_csv(data_dir, encoding="cp949")

        for i in tqdm(os.listdir(self.path + "/data/etf")):
            data_dir = self.path + "/data/etf/" + i
            etf_df = pd.read_csv(data_dir, index_col=0, encoding="cp949")
            etf_preprocess = Indicator(etf_df)
            etf_preprocess.runAll()
            etf_df.to_csv(data_dir, encoding="cp949")
        print("데이터 업데이트가 완료되었습니다.")

    term_list = ["1주 ~ 1개월", "1개월 ~ 6개월", "6개월 ~ 1년", "1년 이상"]
    sector_list = ['건설','금융','기계','IT','운수창고','운수장비',
                   '유통','의약','전기전자','철강금속','화학', '통신', '상관없음']
    know_list = [
        "금융투자상품에 투자해 본 경험이 없음",
        "널리 알려진 금융투자 상품(주식, 채권 및 펀드 등)의 구조 및 위험을 일정 부분 이해하고 있음",
        "널리 알려진 금융투자 상품(주식, 채권 및 펀드 등)의 구조 및 위험을 깊이 있게 이해하고 있음",
        "파생상품을 포함한 대부분의 금융투자상품의 구조 및 위험을 이해하고 있음",
    ]
    risk_list = [
        "예금 또는 적금 수준의 수익률을 기대 / 투자원금의 손실을 원하지 않음",
        "투자원금의 손실 위험을 최소화하고, 안정적인 투자를 목표 / 예금ㆍ적금보다 높은 수익을 위해 단기적인 손실정도는 수용할 수 있고, 자산 중 일부를 위험자산에 투자할 의향이 있음",
        "예금ㆍ적금보다 높은 수익을 기대할 수 있다면 위험을 감수하고 투자할 의향이 있음",
        "투자원금의 보전보다 수익을 추구 / 투자자금의 대부분을 주식, 옵션 등의 위험자산에 투자할 의향이 있음",
        "시장 평균 수익률을 넘어서는 높은 수준의 투자 수익 추구 / 투자자금의 대부분을 주식, 옵션 등의 위험자산에투자할 의향이 있음",
    ]

    style = {"description_width": "initial"}

    capital = widgets.BoundedIntText(
        min=1,
        max=10000,
        value=300,
        continuous_update=True,
        description="투자 금액(만 원)",
        disabled=False,
        style=style,
    )
    term_dropdown = widgets.Dropdown(
        description="투자 기간 ", options=term_list, disabled=False, style=style
    )

    age = widgets.BoundedIntText(
        min=10, max=100, value=20, disabled=False, description="나이 (만)", style=style
    )
    gender_dropdown = widgets.Dropdown(
        description="성별 ", options=["남", "여"], disabled=False, style=style
    )

    income = widgets.FloatText(
        value=100, continuous_update=True, description="월 정기 수입(만 원)", disabled=False, style=style
    )

    sector = widgets.Dropdown(
        options=sector_list,
        description="관심산업분야",
        disabled=False,
        continuous_update=False,
        layout={"width": "max-content"},
        readout=True,
        style=style,
    )
    know = widgets.Dropdown(
        options=know_list,
        description="금융지식수준",
        disabled=False,
        continuous_update=False,
        layout={"width": "max-content"},
        readout=True,
        style=style,
    )
    risk = widgets.Dropdown(
        options=risk_list,
        description="위험추구성향",
        disabled=False,
        continuous_update=False,
        layout={"width": "max-content"},
        readout=True,
        style=style,
    )
    user_buttons = [capital, term_dropdown, age, gender_dropdown, income, sector, know, risk]

    def disposition_viz(self):  # 투자 성향 시각화 및 정보확인

        # 경로
        folder_path = ["age/age_", "period/", "sex/", "tend/"]
        extension_path = ".png"

        # 투자성향 파일명
        if self.user_info[7] == self.risk_list[0]:
            tend = "info5"
        elif self.user_info[7] == self.risk_list[1]:
            tend = "info4"
        elif self.user_info[7] == self.risk_list[2]:
            tend = "info3"
        elif self.user_info[7] == self.risk_list[3]:
            tend = "info2"
        elif self.user_info[7] == self.risk_list[4]:
            tend = "info1"

        # 경로별 이미지 불러오기
        im_tend = Image.open(
            self.path + "/red/interface/image/" + folder_path[3] + tend + extension_path
        )
        font = ImageFont.truetype(self.fontpath, 22)

        # 칼라 설정
        b, g, r, a = 0, 0, 0, 0

        # 이미지에 텍스트 삽임
        draw = ImageDraw.Draw(im_tend)
        draw.text((162, 352), str(self.user_info[2]) + ("세"), font=font, fill=(b, g, r, a))
        draw.text((162, 391), str(self.user_info[3]) + ("자"), font=font, fill=(b, g, r, a))
        draw.text((202, 429.5), str(self.user_info[1]), font=font, fill=(b, g, r, a))
        draw.text((202, 467), str(self.user_info[0]) + ("만원"), font=font, fill=(b, g, r, a))
        draw.text((249.3, 506), str(self.user_info[5]), font=font, fill=(b, g, r, a))
        display(im_tend)

    def portfolio_viz(self):
        self.to_home_button.on_click(self.RED_start)
        
        if (self.user_info[6] == self.know_list[0]) or (self.user_info[6] == self.know_list[1]):
            danger = Image.open(self.path + "/red/interface/image/portfolio/위험고지.png")
            display(danger)
            
        # 관심 산업 상관관계 보여주기
        if self.user_info[5] == self.sector_list[0]:
            s1 = Image.open(self.path + "/red/interface/image/industry/건설양.png")
            s2 = Image.open(self.path + "/red/interface/image/industry/건설음.png")
            display(s1)
            display(s2)
        elif self.user_info[5] == self.sector_list[5]:
            s3 = Image.open(self.path + "/red/interface/image/industry/운수장비양.png")
            display(s3)
        elif self.user_info[5] == self.sector_list[7]:
            s4 = Image.open(self.path + "/red/interface/image/industry/의약음.png")
            display(s4)

        # 포트폴리오 비율
        capital = self.user_info[0] * 10000
        if self.user_info[7] == self.risk_list[0]:
            r1 = 1
            r2 = 0.67
        elif self.user_info[7] == self.risk_list[1]:
            r1 = 0.8
            r2 = 0.4
        elif self.user_info[7] == self.risk_list[2]:
            r1 = 0.6
            r2 = 0.3
        elif self.user_info[7] == self.risk_list[3]:
            r1 = 0.4
            r2 = 0.1
        elif self.user_info[7] == self.risk_list[4]:
            r1 = 0.2
            r2 = 0

        if self.user_info[1] == self.term_list[0] or self.user_info[1] == self.term_list[1]:
            r2 = 0

        real_r0 = int((1 - r1) * 100)
        real_r1 = int((r1 - r2) * 100)
        real_r2 = int(r2 * 100)
        
    
        p_profit = 0 ; p_sigma = 0; p_num = 0; p_ratio = 0;
        for equity in (self.portfolios1, self.portfolios2, self.portfolios3):
            p_num += 1
            if p_num == 1:
                p_ratio = 1-r1
            elif p_num == 2:
                p_ratio = r2
            else:
                p_ratio = r1-r2
            cnt = 0 ; profit = 0; sigma = 0;
            
            for name, info in equity.items():
                cnt += info[0]
                profit += info[1][-2]*info[0]
                sigma += info[1][-1]*info[0]
            if cnt > 0 :
                profit /= cnt; sigma /= cnt;
                
            p_profit += profit *  p_ratio 
            p_sigma += sigma *  p_ratio

        수익률 = round(((1+p_profit/100)**12-1)*100,2)
        표준편차 = round(p_sigma*100,2)

        # 파이 차트 생성
        if r2 == 0:
            ratio = [real_r0, real_r1]
            labels = ["주식", "일반 ETF"]
            colors = ["silver", "gold"]
            wedgeprops = {"width": 0.7, "edgecolor": "w", "linewidth": 5}

            fm.get_fontconfig_fonts()
            font_name = fm.FontProperties(fname=self.fontpath).get_name()
            matplotlib.rc("font", family=font_name)

            fig = plt.figure(figsize=(7, 7))

            plt.pie(
                ratio,
                labels=labels,
                startangle=90,
                autopct="%.0f%%",
                shadow=True,
                textprops={"fontsize": 20},
                colors=colors,
                wedgeprops=wedgeprops,
            )
            if real_r0 == 19:
                plt.legend(labels, fontsize=13, loc="lower left")
            else:
                plt.legend(labels, fontsize=13, loc="upper left")
            plt.savefig(self.path + "/red/interface/image/portfolio/pie_chart.png")
            plt.close()
        else:
            ratio = [real_r0, real_r1, real_r2]
            labels = ["주식", "일반 ETF", "채권 ETF"]
            colors = ["silver", "gold", "lightgray"]
            wedgeprops = {"width": 0.7, "edgecolor": "w", "linewidth": 5}

            fm.get_fontconfig_fonts()
            font_name = fm.FontProperties(fname=self.fontpath).get_name()
            matplotlib.rc("font", family=font_name)

            fig = plt.figure(figsize=(7, 7))

            plt.pie(
                ratio,
                labels=labels,
                startangle=90,
                autopct="%.0f%%",
                shadow=True,
                textprops={"fontsize": 20},
                colors=colors,
                wedgeprops=wedgeprops,
            )
            if real_r0 == 19:
                plt.legend(labels, fontsize=13, loc="lower right")
            else:
                plt.legend(labels, fontsize=13, loc="lower left")
            plt.savefig(self.path + "/red/interface/image/portfolio/pie_chart.png")
            plt.close()

        # 경로별 이미지 불러오기
        im_tend = Image.open(self.path + "/red/interface/image/portfolio/red.png")
        im_chart = Image.open(self.path + "/red/interface/image/portfolio/pie_chart.png")
        font = ImageFont.truetype(self.fontpath, 22)

        # 칼라 설정
        b, g, r, a = 0, 0, 0, 0

        # 이미지에 텍스트 삽입
        draw = ImageDraw.Draw(im_tend)
        draw.text((228, 80.5), "연 " + str(수익률) + "% 내외 추구", font=font, fill=(b, g, r, a))
        draw.text((228, 244), "평균 위험률 연 " + str(표준편차) + "%", font=font, fill=(b, g, r, a))
        draw.text((228, 405), "전체 주식 비중 " + str(real_r0) + "% 수준", font=font, fill=(b, g, r, a))

        # 이미지에 파이차트 삽입
        im_tend.paste(im_chart, (510, 10))

        display(im_tend)