import sys

from bt4.utils.visualize_utils import visualize_trades
from bt4.validator.RegressionTestor import RegressionTestor


def proceed_backtest_with_tid(tid, is_base = True):
    sys.argv = ["BullTraderMain", "bt", "-tid", f"{tid}"]
    print(sys.argv)
    import bt4.exec.BullTraderMain as bm
    ctx, result_file = bm.main(sys.argv)

    # rtestor = RegressionTestor()
    # is_same = rtestor.test_on_the_fly(ctx, result_file,
    #                                   only_for_the_same_cfg = False,
    #                                   show_trading_details = False,
    #                                   is_base = is_base)
    # visualize_trades(result_file)
    return True

def proceed_backtest_with_cfg_module(cfg_module: object) -> object:
    sys.argv = ["BullTraderMain", "bt", "-conf", cfg_module]
    import bt4.exec.BullTraderMain as bm
    ctx, result_file = bm.main(sys.argv)

    rtestor = RegressionTestor()
    is_same = rtestor.test_on_the_fly(ctx, result_file,
                                      only_for_the_same_cfg = False,
                                      show_trading_details = False,
                                      is_base = True)
    # visualize_trades(result_file)
    return is_same
