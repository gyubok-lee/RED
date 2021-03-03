import pandas as pd


class Indicator:
    def __init__(self, df):
        self.df = df
        self.df["pre_close_price"] = self.df["close price"].shift(1).fillna(0)

        self.df["ma5"] = self.df["close price"].rolling(window=5, min_periods=1).mean()
        self.df["ma20"] = self.df["close price"].rolling(window=20, min_periods=1).mean()
        self.df["ma60"] = self.df["close price"].rolling(window=60, min_periods=1).mean()
        self.df["ma120"] = self.df["close price"].rolling(window=120, min_periods=1).mean()
        self.df["amount_ma5"] = self.df["amount"].rolling(window=5, min_periods=1).mean()

    def daily_return(self):
        """일수익률"""
        self.df["일수익률"] = round(
            (self.df["close price"] - self.df["pre_close_price"])
            / self.df["pre_close_price"]
            * 100,
            2,
        )

    def william(self):
        """william's %R"""
        max_price = self.df["close price"].rolling(window=14, min_periods=1).max()
        min_price = self.df["close price"].rolling(window=14, min_periods=1).min()
        self.df["williams"] = (
            (max_price - self.df["close price"]) / (max_price - min_price)
        ) * -100

    def mfi(self):
        self.df["typical_price"] = (
            self.df["high price"] + self.df["low price"] + self.df["close price"]
        ) / 3
        self.df["money_flow"] = self.df["typical_price"] * self.df["amount"]

        self.df["money_flow_positive"] = 0.0
        self.df["money_flow_negative"] = 0.0

        self.df["pre_typical_price"] = self.df["typical_price"].shift(1, fill_value=0)
        self.df.loc[
            self.df["typical_price"] > self.df["pre_typical_price"], "money_flow_positive"
        ] = self.df[self.df["typical_price"] > self.df["pre_typical_price"]]["money_flow"]
        self.df.loc[
            self.df["typical_price"] <= self.df["pre_typical_price"], "money_flow_negative"
        ] = self.df[self.df["typical_price"] <= self.df["pre_typical_price"]]["money_flow"]

        self.df["money_flow_positive_sum"] = (
            self.df["money_flow_positive"].rolling(window=14, min_periods=1).sum()
        )
        self.df["money_flow_negative_sum"] = (
            self.df["money_flow_negative"].rolling(window=14, min_periods=1).sum()
        )
        self.df.loc[
            self.df["money_flow_negative_sum"] == 0.0, "money_flow_negative_sum"
        ] = 0.00001  # 0으로 나누는 상황방지
        self.df["MFI"] = 1 - (
            1 / (1 + (self.df["money_flow_positive_sum"] / self.df["money_flow_negative_sum"]))
        )
        self.df.drop(
            [
                "typical_price",
                "pre_typical_price",
                "money_flow",
                "money_flow_positive",
                "money_flow_negative",
                "money_flow_positive_sum",
                "money_flow_negative_sum",
            ],
            axis=1,
            inplace=True,
        )

    def stochastic(self):
        self.df["fast_k"] = (
            (self.df["close price"] - self.df["low price"].rolling(window=20, min_periods=1).min())
            / (
                self.df["high price"].rolling(window=20, min_periods=1).max()
                - self.df["low price"].rolling(window=20, min_periods=1).min()
            )
        ) * 100

        self.df["slow_k"] = self.df["fast_k"].rolling(window=20, min_periods=1).mean()
        self.df["slow_d"] = self.df["slow_k"].rolling(window=20, min_periods=1).mean()

    def std(self):
        """20일 표준편차"""
        self.df["std"] = self.df["close price"].rolling(window=20, min_periods=1).std()

    def sigma(self):
        """20일 Sigma값"""
        self.df["sigma"] = (self.df["close price"] - self.df["ma20"]) / self.df["std"]

    def rsi(self):
        self.df["u"] = self.df.apply(
            lambda x: max(x["close price"] - x["pre_close_price"], 0), axis=1
        )
        self.df["d"] = self.df.apply(
            lambda x: max(x["pre_close_price"] - x["close price"], 0), axis=1
        )

        self.df["au"] = self.df["u"].rolling(window=20, min_periods=1).mean()
        self.df["ad"] = self.df["d"].rolling(window=20, min_periods=1).mean()
        self.df["rs"] = self.df["au"] / self.df["ad"]
        self.df["rsi"] = self.df["rs"] / (1 + self.df["rs"])
        self.df.drop(["u", "d", "au", "ad", "rs"], axis=1, inplace=True)

    def runAll(self):
        self.daily_return()
        self.william()
        self.mfi()
        self.stochastic()
        self.std()
        self.sigma()
        self.rsi()
