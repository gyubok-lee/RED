#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from sklearn.preprocessing import MinMaxScaler
import pandas as pd
import os

def industry_analysis():
    
    # MinMaxScaler 1 to 100
    scaler = MinMaxScaler(feature_range=(0, 100))
    
    def arng(data):
        data = data.split(', ')
        data = sorted(data)
        return data
    
    def mk_data(아이템, i, 아이템데이터):
        for j in 아이템:
            j1 = str(j)+str('.csv')
            if j1 in i:
                data = pd.read_csv('./data/stock/'+str(i),encoding='cp949')
                data = data[['close price']]
                df = data.copy()
                fitted = scaler.fit(data)
                data = scaler.transform(data)
                data = pd.DataFrame(data, columns=df.columns, index=list(df.index.values))
                data[str(아이템)] = data['close price']
                data = data[str(아이템)]
                아이템데이터 = pd.concat([아이템데이터,data],axis=1)
        return 아이템데이터
    
    def 산업비교(a, b):
        결과 = []
        for i in range(5):
            for j in range(5):
                저장 = pd.concat([a.iloc[:,i],b.iloc[:,j]],axis=1)
                결과.append(저장.corr().iloc[0,1])
        return sum(결과)/len(결과)
    
    sector_list = ['건설','금융','기계','IT','운수창고','운수장비','유통','의약','전기전자','철강금속','화학']
    건설 = '대우건설, 대림산업, 현대건설, GS건설, HDC현대산업개발'
    금융 = 'KB금융, 삼성생명, 신한지주, SK, LG'
    기계 = '씨에스윈드, 두산중공업, 두산밥캣, 두산인프라코어, 한온시스템'
    IT = '엔씨소프트, 삼성에스디에스, SK바이오팜, NAVER, 카카오'
    운수창고 = '대한항공, 현대글로비스, 한진칼, CJ대한통운, HMM'
    운수장비 = '기아차, 현대모비스, 현대차, 삼성중공업, 만도'
    유통 = '동서, 이마트, 삼성물산, 호텔신라, 롯데쇼핑'
    의약 = '신풍제약, 유한양행, 삼성바이오로직스, 셀트리온, 녹십자'
    전기전자 = '삼성전자, SK하이닉스, 삼성SDI, 삼성전기, LG전자'
    철강금속 = 'POSCO, 현대제철, 고려아연, KG동부제철, 영풍'
    화학 = 'LG화학, 아모레퍼시픽, LG생활건강, SK이노베이션, 롯데케미칼'
    
    건설 = arng(건설)
    금융 = arng(금융)
    기계 = arng(기계)
    IT = arng(IT)
    운수창고 = arng(운수창고)
    운수장비 = arng(운수장비)
    유통 = arng(유통)
    의약 = arng(의약)
    전기전자 = arng(전기전자)
    철강금속 = arng(철강금속)
    화학 = arng(화학)
    
    건설데이터 = pd.DataFrame()
    금융데이터 = pd.DataFrame()
    기계데이터 = pd.DataFrame()
    IT데이터 = pd.DataFrame()
    운수창고데이터 = pd.DataFrame()
    운수장비데이터 = pd.DataFrame()
    유통데이터 = pd.DataFrame()
    의약데이터 = pd.DataFrame()
    전기전자데이터 = pd.DataFrame()
    철강금속데이터 = pd.DataFrame()
    화학데이터 = pd.DataFrame()
    
    for i in os.listdir("./data/stock"):
        건설데이터 = mk_data(건설, i, 건설데이터)
        금융데이터 = mk_data(금융, i, 금융데이터)
        기계데이터 = mk_data(기계, i, 기계데이터)
        IT데이터 = mk_data(IT, i, IT데이터)
        운수창고데이터 = mk_data(운수창고, i, 운수창고데이터)
        운수장비데이터 = mk_data(운수장비, i, 운수장비데이터)
        유통데이터 = mk_data(유통, i, 유통데이터)
        의약데이터 = mk_data(의약, i, 의약데이터)
        전기전자데이터 = mk_data(전기전자, i, 전기전자데이터)
        철강금속데이터 = mk_data(철강금속, i, 철강금속데이터)
        화학데이터 = mk_data(화학, i, 화학데이터)
        
    last = []

    last.append(산업비교(건설데이터, 금융데이터))
    last.append(산업비교(건설데이터, 기계데이터))
    last.append(산업비교(건설데이터, IT데이터))
    last.append(산업비교(건설데이터, 운수창고데이터))
    last.append(산업비교(건설데이터, 운수장비데이터))
    last.append(산업비교(건설데이터, 유통데이터))
    last.append(산업비교(건설데이터, 의약데이터)) # 6 : -0.43
    last.append(산업비교(건설데이터, 전기전자데이터))
    last.append(산업비교(건설데이터, 철강금속데이터)) # 8 : 0.41
    last.append(산업비교(건설데이터, 화학데이터))

    last.append(산업비교(금융데이터, 기계데이터))
    last.append(산업비교(금융데이터, IT데이터))
    last.append(산업비교(금융데이터, 운수창고데이터))
    last.append(산업비교(금융데이터, 운수장비데이터))
    last.append(산업비교(금융데이터, 유통데이터))
    last.append(산업비교(금융데이터, 의약데이터))
    last.append(산업비교(금융데이터, 전기전자데이터))
    last.append(산업비교(금융데이터, 철강금속데이터))
    last.append(산업비교(금융데이터, 화학데이터))

    last.append(산업비교(기계데이터, IT데이터))
    last.append(산업비교(기계데이터, 운수창고데이터))
    last.append(산업비교(기계데이터, 운수장비데이터))
    last.append(산업비교(기계데이터, 유통데이터))
    last.append(산업비교(기계데이터, 의약데이터))
    last.append(산업비교(기계데이터, 전기전자데이터))
    last.append(산업비교(기계데이터, 철강금속데이터))
    last.append(산업비교(기계데이터, 화학데이터))

    last.append(산업비교(IT데이터, 운수창고데이터))
    last.append(산업비교(IT데이터, 운수장비데이터))
    last.append(산업비교(IT데이터, 유통데이터))
    last.append(산업비교(IT데이터, 의약데이터))
    last.append(산업비교(IT데이터, 전기전자데이터))
    last.append(산업비교(IT데이터, 철강금속데이터))
    last.append(산업비교(IT데이터, 화학데이터))

    last.append(산업비교(운수창고데이터, 운수장비데이터))
    last.append(산업비교(운수창고데이터, 유통데이터))
    last.append(산업비교(운수창고데이터, 의약데이터))
    last.append(산업비교(운수창고데이터, 전기전자데이터))
    last.append(산업비교(운수창고데이터, 철강금속데이터))
    last.append(산업비교(운수창고데이터, 화학데이터))

    last.append(산업비교(운수장비데이터, 유통데이터))
    last.append(산업비교(운수장비데이터, 의약데이터)) # 41 : -0.39
    last.append(산업비교(운수장비데이터, 전기전자데이터))
    last.append(산업비교(운수장비데이터, 철강금속데이터))
    last.append(산업비교(운수장비데이터, 화학데이터))

    last.append(산업비교(유통데이터, 의약데이터))
    last.append(산업비교(유통데이터, 전기전자데이터))
    last.append(산업비교(유통데이터, 철강금속데이터))
    last.append(산업비교(유통데이터, 화학데이터))

    last.append(산업비교(의약데이터, 전기전자데이터))
    last.append(산업비교(의약데이터, 철강금속데이터)) # 50 : -0.31
    last.append(산업비교(의약데이터, 화학데이터))

    last.append(산업비교(전기전자데이터, 철강금속데이터))
    last.append(산업비교(전기전자데이터, 화학데이터))

    last.append(산업비교(철강금속데이터, 화학데이터))
    
    plus_corr = []
    minus_corr = []
    
    cnt1 = 0
    cnt2 = 0
    
    for i in range(len(last)):
        if last[i] >= 0.4:
            plus_corr.append([last[i],i])
            #print('양의 상관관계 :',last[i],'   ',i,'\n')
            cnt1 = cnt1+1
        if last[i] <= -0.3:
            minus_corr.append([last[i],i])
            #print('음의 상관관계 :',last[i],'   ',i,'\n')
            cnt2 = cnt2+1

    print("산업간 양(+)의 상관관계가 총 {}개 발견되었습니다.\n".format(cnt1))
    print("산업간 음(-)의 상관관계가 총 {}개 발견되었습니다.".format(cnt2))
            
    return