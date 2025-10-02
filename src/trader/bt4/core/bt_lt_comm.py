from bt4.Constants import CandleType


def filter_out_unused_markets(quote, ex_types, markets) :
    for ex_type in ex_types :
        market_ticks = quote.get_market_ticks(ex_type)

        to_be_removed_markets = []
        if market_ticks is not None :
            for market in market_ticks :
                if market not in markets :
                    to_be_removed_markets.append(market)

            for tbrm in to_be_removed_markets :
                market_ticks.pop(tbrm)

        cdl_types = quote.get_candle_types(ex_type)
        if cdl_types is not None :
            for cdl_type in cdl_types :
                to_be_removed_cdl_markets = []
                for market in cdl_types[cdl_type] :
                    if market not in markets :
                        to_be_removed_cdl_markets.append(market)

                for tbrcm in to_be_removed_cdl_markets :
                    cdl_types[cdl_type].pop(tbrcm)
    return quote

def is_simul_time(time_dt, simul_times):
    for s_time in simul_times:
        if s_time[0] == time_dt.hour and s_time[1] == time_dt.minute:
            return True
    return False

def is_my_tick(time_pdt, cdl_type, tr_times, tr_int_times) :
    my_tick = True
    if cdl_type != CandleType.MINUTES_1 :
        if cdl_type == CandleType.HOUR :
            if time_pdt.minute != 59 :
                my_tick = False

        elif cdl_type == CandleType.HOUR4 :
            remainder = time_pdt.minute % cdl_type.value
            if not (time_pdt.hour in [0, 4, 8, 12, 16, 20] and remainder == 59) :
                my_tick = False

        elif cdl_type is CandleType.DAYS :
            remainder = time_pdt.minute % cdl_type.value
            if not (time_pdt.hour == 8 and remainder == 59) :
                my_tick = False

        else :
            remainder = time_pdt.minute % cdl_type.value
            if remainder != (cdl_type.value - 1) :
                my_tick = False

    if cdl_type != CandleType.MINUTES_1 and \
            len(tr_times) != 0 and not is_simul_time(time_pdt, tr_int_times) :
        my_tick = False

    return my_tick

