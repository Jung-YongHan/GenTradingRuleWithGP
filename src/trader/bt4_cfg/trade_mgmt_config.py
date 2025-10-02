from bt4.Constants import R, AssetMgrType

r = R()

trade_tactic = {}

## Used in ws_day_fixed, day_trading_arima_labeled, frl_2022_1_price_fixed, frl_2022_2_macd_fixed
# frl_2022_3_rsi_fixed, frl_2022_4_plus_minus_di_fixed
trade_tactic['net_fixed'] = {
      r.AM.AM_TYPE : AssetMgrType.FIXED,
      r.AM.AM_FIXED_TRADE_RATIO : 0.4,
      r.AM.REBAL_TIMES : ['08:59']
}

## Used in ws_day_hdg_fixed
trade_tactic['hdg_fixed'] = {
      r.AM.AM_TYPE : AssetMgrType.FIXED_HDGE,
      r.AM.AM_FIXED_TRADE_RATIO : 0.4,
      r.AM.AM_TIMEFRAMES : ['07:59', '08:59', '09:59', '10:59', '11:59', '12:59',  ## For Hedging
                               '13:59', '14:59', '15:59', '16:59', '17:59', '18:59',
                               '19:59', '20:59', '21:59', '22:59', '23:59', '00:59',
                               '01:59', '02:59', '03:59', '04:59', '05:59', '06:59'],
      r.AM.REBAL_TIMES : ['08:59']
}

## Used in  ws_day_vol, sws_4h_vol, sws_day_vol, sws_ma_crossover_day_vol,
# sws_sell_1h_ta_comb_vol, composite_bull_bear_market, ma_cross_over_vol,
# swkim_1_vol, ttrading_origin_vol, ttrading_vol, vol_bout_sws_vol, vol_bout_vol
# vol_brk_thr_sws_vol
trade_tactic['net_vol'] = {
      r.AM.AM_TYPE : AssetMgrType.VOLATILITY,
      r.AM.AM_VOL_TARGET : 0.04,
      r.AM.AM_VOL_TAI : 'vol5',
      r.AM.REBAL_TIMES: ['08:59']
}

## Used in frl_2022_5_super_plus_minus_di_vol, ptrn_1_combination_vol
trade_tactic['net_vol_2'] = {
      'overide_from': 'net_vol',
      r.AM.AM_VOL_TAI : 'vol5_4h',
}

## Used in frl_2022_5_super_plus_minus_di_vol, ptrn_1_combination_vol
trade_tactic['net_vol_3'] = {
      'overide_from': 'net_vol',
      r.AM.AM_VOL_TARGET : 0.02,
}

## Used in sws_day_hdg_vol
trade_tactic['hdg_vol'] = {
      r.AM.AM_TYPE : AssetMgrType.VOLATILITY_HDGE,
      r.AM.AM_VOL_TARGET : 0.04,
      r.AM.AM_VOL_TAI : 'vol5',
      r.AM.AM_TIMEFRAMES : ['08:59', '17:59'],
      r.AM.REBAL_TIMES : ['08:59']
}

## Used in ws_day_hdg_vol
trade_tactic['hdg_vol_2'] = {
      'overide_from' : 'hdg_vol1',
      r.AM.AM_TIMEFRAMES : ['01:59', '08:59'],
}

## Used in sws_day_hdg_vol_ema, ttrading_hdg_vol
trade_tactic['hdg_vol_3'] = {
      'overide_from': 'hdg_vol1',
      r.AM.AM_TIMEFRAMES : ['07:59', '17:59'],
}

## Used in sws_ma_crossover_hdg_vol, vol_bbout_hdg_vol
trade_tactic['hdg_vol_4'] = {
      'overide_from': 'hdg_vol1',
      r.AM.AM_TIMEFRAMES : ['08:59', '12:59', '16:59', '20:59'],
}

## Used in composite_bull_bear_market_hdg, ma_cross_over_hdg_vol
trade_tactic['hdg_vol_5'] = {
      'overide_from': 'hdg_vol1',
      r.AM.AM_TIMEFRAMES : ['08:59'],
}

## Used in swkim_1_hdg_vol
trade_tactic['hdg_vol_6'] = {
      'overide_from': 'hdg_vol1',
      r.AM.AM_TIMEFRAMES : ['08:59', '16:59'],
}

## Used in vol_bout_sws_hdg_vol, vol_bout_ws_hdg_vol
trade_tactic['hdg_vol_7'] = {
      'overide_from': 'hdg_vol1',
      r.AM.AM_TIMEFRAMES : ['07:59', '08:59', '09:59', '10:59', '11:59', '12:59',    ## For Hedging
                        '13:59', '14:59', '15:59', '16:59', '17:59', '18:59',
                        '19:59', '20:59', '21:59', '22:59', '23:59', '00:59',
                        '01:59', '02:59', '03:59', '04:59', '05:59', '06:59']
}

