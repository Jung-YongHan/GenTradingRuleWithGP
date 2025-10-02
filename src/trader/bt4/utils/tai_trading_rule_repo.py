import talib

from bt4.Constants import QItem, CandleType, Ary

############################################################################################
## MACD
TAI_macd = ['macd', [12, 26, 9], CandleType.DAYS, [QItem.close], Ary.Nary]
TAI_macd1 = ['macd', [5, 12, 3], CandleType.DAYS, [QItem.close], Ary.Nary]
TAI_macd2 = ['macd', [20, 42, 15], CandleType.DAYS, [QItem.close], Ary.Nary]

def macd_buy(mkt_tais, tmgr, market, price, time_dt) :
    macd_buy_signal = False
    macd, macd_sig, _ = mkt_tais[market]["macd"]
    desc = ""
    if macd > macd_sig :
        macd_buy_signal = True

    desc += f"macd({macd_buy_signal}) = macd({macd}) > macd_sig({macd_sig}), "
    return macd_buy_signal, desc

def macd_sell(mkt_tais, tmgr, market, price, time_dt) :
    macd_sell_signal = False
    macd, macd_sig, _ = mkt_tais[market]["macd"]
    desc = ""
    if macd < macd_sig :
        macd_sell_signal = True
    desc += f"macd({macd_sell_signal}) = macd({macd}) < macd_sig({macd_sig}), "
    return macd_sell_signal, desc

############################################################################################
## IC
TAI_ic = ['ic', [52], CandleType.DAYS, [QItem.high, QItem.low], Ary.Unary]

def ic_buy(mkt_tais, tmgr, market, price, time_dt) :
    desc = ""
    ic_signal = False  # True to enable, False for disable
    ic = mkt_tais[market]["ic"]
    if price > ic :
        ic_signal = True
    desc += f"ic({ic_signal}) price({price}) > ic({ic}), "
    return ic_signal, desc

def ic_sell(mkt_tais, tmgr, market, price, time_dt) :
    desc = ""
    ic_signal = False
    ic = mkt_tais[market]["ic"]
    if price < ic :
        ic_signal = False  # True to enable, False for disable
    desc += f"ic({ic_signal}) price({price}) < ic({ic}), "
    return ic_signal, desc

############################################################################################
## CMF
TAI_cmf = ['cmf', [21], CandleType.DAYS, [QItem.high, QItem.low,QItem.close,QItem.vol], Ary.Unary]

def cmf_buy(mkt_tais, tmgr, market, price, time_dt) :
    desc = ""
    cmf_signal = True  # True for disable, False for enable
    cmf = mkt_tais[market]["cmf"]
    if cmf > 0 :
        cmf_signal = True
    desc += f"cmf({cmf_signal}) cmf({cmf}) > 0, "
    return cmf_signal, desc

def cmf_sell(mkt_tais, tmgr, market, price, time_dt) :
    desc = ""
    cmf_signal = False
    cmf = mkt_tais[market]["cmf"]
    if cmf < 0 :
        cmf_signal = False  # True to enable, False for disable
    desc += f"cmf({cmf_signal}) cmf({cmf}) < 0, "
    return cmf_signal, desc

############################################################################################
## IC1
TAI_ic1 = ['ic1', [9, 26], CandleType.DAYS, [QItem.high, QItem.low], Ary.Unary]

def ic1_buy(mkt_tais, tmgr, market, price, time_dt) :
    ic1_signal = False
    desc = ""
    ic1 = mkt_tais[market]["ic1"]
    if price > ic1 :
        ic1_signal = True  # True to enable, False for disable
    desc += f"ic1({ic1_signal}) price({price}) > ic1({ic1}), "
    return ic1_signal, desc

def ic1_sell(mkt_tais, tmgr, market, price, time_dt) :
    desc = ""
    ic1_signal = False
    ic1 = mkt_tais[market]["ic1"]
    if price < ic1 :
        ic1_signal = True
    desc += f"ic1({ic1_signal}) price({price}) < ic1({ic1}), "
    return ic1_signal, desc

############################################################################################
## Moving AVERAGE
TAI_ma1 = ['sma', [3], CandleType.DAYS, [QItem.close], Ary.Unary]
TAI_ma2 = ['sma', [5], CandleType.DAYS, [QItem.close], Ary.Unary]
TAI_ma3 = ['sma', [10], CandleType.DAYS, [QItem.close], Ary.Unary]
TAI_ma4 = ['sma', [20], CandleType.DAYS, [QItem.close], Ary.Unary]
TAI_ma5 = ['sma', [30], CandleType.DAYS, [QItem.close], Ary.Unary]

TAI_ema1 = ['ema', [3], CandleType.DAYS, [QItem.close], Ary.Unary]
TAI_ema2 = ['ema', [5], CandleType.DAYS, [QItem.close], Ary.Unary]
TAI_ema3 = ['ema', [10], CandleType.DAYS, [QItem.close], Ary.Unary]
TAI_ema4 = ['ema', [20], CandleType.DAYS, [QItem.close], Ary.Unary]
TAI_ema5 = ['ema', [30], CandleType.DAYS, [QItem.close], Ary.Unary]

TAI_wma1 = ['wma', [3], CandleType.DAYS, [QItem.close], Ary.Unary]
TAI_wma2 = ['wma', [5], CandleType.DAYS, [QItem.close], Ary.Unary]
TAI_wma3 = ['wma', [10], CandleType.DAYS, [QItem.close], Ary.Unary]
TAI_wma4 = ['wma', [20], CandleType.DAYS, [QItem.close], Ary.Unary]
TAI_wma5 = ['wma', [30], CandleType.DAYS, [QItem.close], Ary.Unary]

def ma_buy(mkt_tais, tmgr, market, price, time_dt) :
    buy_signal = False
    desc = ""
    ma = mkt_tais[market]["ma"]
    if price > ma :
        buy_signal = True  # True to enable, False for disable
    desc += f"ma({ma}) price({price}) > ma({ma}), "
    return buy_signal, desc

def ma_sell(mkt_tais, tmgr, market, price, time_dt) :
    desc = ""
    sell_signal = False
    ma = mkt_tais[market]["ma"]
    if price < ma :
        sell_signal = True
    desc += f"ma({sell_signal}) price({price}) < ma({ma}), "
    return sell_signal, desc

############################################################################################
## PDI / MDI
TAI_pdi = ['PLUS_DI', [14], CandleType.HOUR4, [QItem.high, QItem.low, QItem.close], Ary.Unary]
TAI_mdi = ['MINUS_DI', [14], CandleType.HOUR4, [QItem.high, QItem.low, QItem.close], Ary.Unary]

def pmdi_buy(mkt_tais, tmgr, market, price, time_dt) :
    buy_signal = False
    desc = ""
    pdi = mkt_tais[market]['pdi']
    mdi = mkt_tais[market]['mdi']

    if pdi > mdi :
        buy_signal = True  # True to enable, False for disable
    desc += f"pmdi({buy_signal}) pdi({pdi}) > mdi({mdi}), "
    return buy_signal, desc

def pmdi_sell(mkt_tais, tmgr, market, price, time_dt) :
    desc = ""
    sell_signal = False
    pdi = mkt_tais[market]['pdi']
    mdi = mkt_tais[market]['mdi']

    if pdi < mdi :
        sell_signal = True
    desc += f"pmdi({sell_signal}) pdi({pdi}) < mdi({mdi}), "
    return sell_signal, desc

############################################################################################
## CCI
TAI_cci = ['CCI', [20], CandleType.DAYS_TF, [QItem.high, QItem.low, QItem.close], Ary.Unary]
TAI_cci2 = ['CCI', [14], CandleType.DAYS_TF, [QItem.high, QItem.low, QItem.close], Ary.Unary]

def cci_buy(mkt_tais, tmgr, market, price, time_dt) :
    buy_signal = False
    desc = ""
    cci = mkt_tais[market]['cci']

    if cci > -100 :
        buy_signal = True  # True to enable, False for disable
    desc += f"cci({buy_signal}) cci({cci}) > -100, "
    return buy_signal, desc

def cci_sell(mkt_tais, tmgr, market, price, time_dt) :
    desc = ""
    sell_signal = False
    cci = mkt_tais[market]['cci']

    if cci > 100 :
        sell_signal = True
    desc += f"cci({sell_signal}) cci({cci}) < 100, "
    return sell_signal, desc

############################################################################################
## Parabolic SAR
TAI_pasr = ['sar', [0.02, 0.2], CandleType.DAYS, [QItem.high, QItem.low], Ary.Unary]
def psar_buy(mkt_tais, tmgr, market, price, time_dt) :
    buy_signal = False
    desc = ""
    psar = mkt_tais[market]['psar']
    if price > psar :
        buy_signal = True
    desc += f"psar({buy_signal}) price({price}) > psar({psar}), "
    return buy_signal, desc

def psar_sell(mkt_tais, tmgr, market, price, time_dt) :
    sell_signal = False
    desc = ""
    psar = mkt_tais[market]['psar']
    if price < psar :
        sell_signal = True
    desc = f"psar({sell_signal}) price({price}) < psar({psar}), "
    return sell_signal, desc

############################################################################################
## RSI
TAI_rsi = ['rsi', [14], CandleType.DAYS, [QItem.close], Ary.Unary]

def rsi_buy(mkt_tais, tmgr, market, price, time_dt) :
    buy_signal = False
    desc = ""
    rsi = mkt_tais[market]['rsi']
    if rsi < 30 :
        buy_signal = True
    desc += f"rsi({buy_signal}) rsi({rsi}) < 30, "
    return buy_signal, desc

def rsi_sell(mkt_tais, tmgr, market, price, time_dt) :
    sell_signal = False
    desc = ""
    rsi = mkt_tais[market]['rsi']
    if rsi > 70 :
        sell_signal = True
    desc = f"rsi({sell_signal}) rsi({rsi}) < 70, "
    return sell_signal, desc

############################################################################################
## trix
TAI_trix = ['TRIX', [30], CandleType.DAYS, [QItem.close], Ary.Unary]
TAI_trix2 = ['TRIX', [18], CandleType.DAYS, [QItem.close], Ary.Unary]


def trix_buy(mkt_tais, tmgr, market, price, time_dt) :
    buy_signal = False
    desc = ""
    trix = mkt_tais[market]['trix'] * 100
    if trix > 0 :
        buy_signal = True
    desc += f"trix({buy_signal}) trix({trix}) > 0, "
    return buy_signal, desc

def trix_sell(mkt_tais, tmgr, market, price, time_dt) :
    sell_signal = False
    desc = ""
    trix = mkt_tais[market]['trix'] * 100
    if trix < 0 :
        sell_signal = True
    desc = f"trix({sell_signal}) trix({trix}) < 70, "
    return sell_signal, desc

############################################################################################
## Stochastic talib.STOCH()
TAI_stoch = ['stoch', [14, 1, 0, 3, 0], CandleType.DAYS, [QItem.high, QItem.low, QItem.close], Ary.Nary]
def stoch_buy(mkt_tais, tmgr, market, price, time_dt) :
    buy_signal = False
    desc = ""
    k, d = mkt_tais[market]['stoch']
    if k > d :
        buy_signal = True
    desc += f"stoch({buy_signal}) k({k}) > d({d}), "
    return buy_signal, desc

def stoch_sell(mkt_tais, tmgr, market, price, time_dt) :
    sell_signal = False
    desc = ""
    k, d = mkt_tais[market]['stoch']
    if k < d :
        sell_signal = True
    desc = f"stoch({sell_signal}) k({k}) < d({d}), "
    return sell_signal, desc

def stoch_buy2(mkt_tais, tmgr, market, price, time_dt) :
    buy_signal = False
    desc = ""
    k, d = mkt_tais[market]['stoch']
    if k > 80 :
        buy_signal = True
    desc += f"stoch2({buy_signal}) k({k}) > 80, "
    return buy_signal, desc

def stoch_sell2(mkt_tais, tmgr, market, price, time_dt) :
    sell_signal = False
    desc = ""
    k, d = mkt_tais[market]['stoch']
    if k < 20 :
        sell_signal = True
    desc = f"stoch2({sell_signal}) k({k}) < 20, "
    return sell_signal, desc

############################################################################################
##  Williams' %R talib.WILLR()
TAI_willr = ['willr', [], CandleType.DAYS, [QItem.high, QItem.low, QItem.close], Ary.Unary]

def willr_buy(mkt_tais, tmgr, market, price, time_dt) :
    buy_signal = False
    desc = ""
    wr = mkt_tais[market]['willr']
    if wr < -80 :
        buy_signal = True
    desc += f"wr({buy_signal}) wr({wr}) > -80, "
    return buy_signal, desc

def willr_sell(mkt_tais, tmgr, market, price, time_dt) :
    sell_signal = False
    desc = ""
    wr = mkt_tais[market]['willr']
    if wr > -20 :
        sell_signal = True
    desc = f"wr({sell_signal}) wr({wr}) > -20, "
    return sell_signal, desc

############################################################################################
##  MFI talib.MFI()

TAI_mfi = ['mfi', [], CandleType.DAYS, [QItem.high, QItem.low, QItem.close, QItem.vol], Ary.Unary]
def mfi_buy(mkt_tais, tmgr, market, price, time_dt) :
    buy_signal = False
    desc = ""
    mfi = mkt_tais[market]['mfi']
    if mfi < 20 :
        buy_signal = True
    desc += f"mfi({buy_signal}) mfi({mfi}) > -80, "
    return buy_signal, desc

def mfi_sell(mkt_tais, tmgr, market, price, time_dt) :
    sell_signal = False
    desc = ""
    mfi = mkt_tais[market]['mfi']
    if mfi > 80 :
        sell_signal = True
    desc = f"mfi({mfi}) mfi({mfi}) > -20, "
    return sell_signal, desc