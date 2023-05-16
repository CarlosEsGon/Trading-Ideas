# region imports
from AlgorithmImports import *
# endregion

#Strategy implemented in Quantconnect backtesting environment
#Tail Risk Hedging strategy - allocate 1% of capital to deep out of the money puts with a time to maturity of more than 180 days
#to protect against sudden and unexpcected drawdowns due to unpredictable events (Black Swans)
#Strategy based on Nicholas Nassim Taleb´s ideas

class SleepyMagentaAlbatross(QCAlgorithm):

    def Initialize(self):
        self.SetStartDate(2015, 1, 1)  # Set Start Date
        self.SetCash(100000)  # Set Strategy Cash
        spy = self.AddEquity("SPY", Resolution.Minute)
        spy.SetDataNormalizationMode(DataNormalizationMode.Raw) #Necessary data mode is Raw as opposed to the default adjusted


        self.spy = spy.Symbol #storing the SPY Symbol for latter use - using symbols in Quantconnect is more reliable
        self.contract = None #algorithm starts with 0 put contracts


    def OnData(self, data):
        #if the portfolio allocation to SPY is not invested, allocate 99% of capital
        if not self.Portfolio[self.spy].Invested:
            self.SetHoldings(self.spy, 0.99)

        #if there are no put contracts, select the put options from our function contract_selector()
        if self.contract is None:
            self.contract = self.contract_selector()
            return

        #if the put contract time to maturity is less than 90 days, liquidate the put contract
        if (self.contract.ID.Date - self.Time).days <= 90:
            self.Liquidate(self.contract)
            self.RemoveSecurity(self.contract) #remove the contract for our data feed since it is irrelevant
            self.contract = None
            return

        #if the portfolio allocation to Put Options is not invested, allocate 1% of capital
        if not self.Portfolio[self.contract].Invested:
            self.SetHoldings(self.contract, 0.01)


        if self.Securities[self.spy].Price < self.contract.ID.StrikePrice * 1.3:
            self.Liquidate(self.contract)
            self.RemoveSecurity(self.contract)


    def contract_selector(self):
        """Using Option Chain Provider as we have a narrow scope of options that we want"""
        target_strike = self.Securities[self.spy].Price * 0.6 - (self.Securities[self.spy].Price * 0.6)%5

        #returns the option contract list for SPY ETF
        contracts = self.OptionChainProvider.GetOptionContractList(self.spy, self.Time)

        #selects all of the contracts that are puts
        puts = [contract for contract in contracts if contract.ID.OptionRight == OptionRight.Put]

        puts = sorted(sorted(puts, key = lambda x:  x.ID.Date, reverse= True), key = lambda x: x.ID.StrikePrice)

        puts = [put for put in puts if put.ID.StrikePrice == target_strike]
        puts = [put for put in puts if 180 < (put.ID.Date - self.Time).days < 360]

        if len(puts) == 0:
            return None
        self.AddOptionContract(puts[0], Resolution.Minute)
        return puts[0]
