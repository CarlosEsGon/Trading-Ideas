#Strategy implemented in QuantConnect backtesting environment

# region imports
from AlgorithmImports import *
# endregion

class FatLightBrownChinchilla(QCAlgorithm):

    def Initialize(self):
        self.SetStartDate(2010, 1, 1)  # Set Start Date
        self.SetEndDate(2021, 1, 1)
        self.SetCash(100000)  # Set Strategy Cash
        self.SetWarmup(90)

        periods = (30, 90)

        self.trade = SymbolData(self, self.AddEquity("XHB").Symbol, periods)
        self.indicator = SymbolData(self, self.AddEquity("WOOD").Symbol, periods)

    def OnData(self, data):
        if not self.indicator.is_ready():
            return

        if self.indicator.short_ema.Current.Value > self.indicator.long_ema.Current.Value:
            # long
            if self.Portfolio[self.trade.symbol].IsShort or not self.Portfolio.Invested:
                self.SetHoldings(self.trade.symbol, 1)
        if self.indicator.short_ema.Current.Value < self.indicator.long_ema.Current.Value:
            # short
            if self.Portfolio[self.trade.symbol].IsLong or not self.Portfolio.Invested:
                self.SetHoldings(self.trade.symbol, -1)

class SymbolData:

    def __init__(self, algorithm, symbol, periods):
        self.symbol = symbol
        self.short_ema = algorithm.EMA(self.symbol, periods[0], Resolution.Daily )
        self.long_ema = algorithm.EMA(self.symbol, periods[1], Resolution.Daily )

    def is_ready(self):
        return self.short_ema.IsReady and self.long_ema.IsReady
