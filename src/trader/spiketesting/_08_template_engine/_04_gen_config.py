import unittest

from bt4.Constants import CandleType, QItem


class MyTestCase(unittest.TestCase) :
    def test_gen_config(self) :
        from jinja2 import Environment, FileSystemLoader

        strategy_name = "sws_day_hdg_vol_rule"
        environment = Environment(loader = FileSystemLoader("templates/"))
        results_filename = f"{strategy_name}.py"
        results_template = environment.get_template("config_template.jinja2")

        context = {
            "stgy_name"     : "SuperWinningSession_Rule_Hedge",
            "module_name"   : "SuperWinningSessionStrategy",
            "bt_start"      : "2022-06-22T08:59:00",
            "bt_end"        : "2023-11-05T08:59:00",
            "markets"       : ['KRW-BTC', 'KRW-ETH', 'KRW-XRP'],
            "cdl_type"      : CandleType.HOUR,
            "vola"          : {"support" : True,
                               "vol_tgt" : 0.04,
                               },
            "timeframe"     : {"support"    : True,
                               "timeframes" : ['08:59', '17:59'],
                               "timegap"    : 1
                               },

            "fixed"         : {"support"     : True,
                               "hdge"        : True,
                               "trade_ratio" : 0.4},

            "stop_loss"     : {"support" : False,
                               "ratio"   : -0.04},
            "trailing_stop" : {"support" : False,
                               "ratio"   : -0.02},
            "take_profit"   : {"support" : False,
                               "ratio"   : 0.07},
            "vars"          : {
                "ma1" : {
                    "func"     : "sma",
                    "params"   : [3],
                    "cdl_type" : CandleType.DAYS_TF,
                    "sources"  : [QItem.close]
                },
                "ma2" : {
                    "func"     : "sma",
                    "params"   : [5],
                    "cdl_type" : CandleType.DAYS_TF,
                    "sources"  : [QItem.close]
                },
                "ma3" : {
                    "func"     : "sma",
                    "params"   : [10],
                    "cdl_type" : CandleType.DAYS_TF,
                    "sources"  : [QItem.close]
                },
                "ma4" : {
                    "func"     : "sma",
                    "params"   : [20],
                    "cdl_type" : CandleType.DAYS_TF,
                    "sources"  : [QItem.close]
                }
            }
        }

        with open(results_filename, mode = "w", encoding = "utf-8") as results :
            results.write(results_template.render(context))
            print(f"... wrote {results_filename}")

    def test_gen_strategy(self) :
        from jinja2 import Environment, FileSystemLoader

        import uuid
        my_id = str(uuid.uuid4())
        stgy_id = str(uuid.uuid4())

        context = {
            "id" : my_id,
            "stgy_id" : stgy_id,
            "stgy_name"     : "SuperWinningSession_Rule_Hedge",
            "module_name"   : "SuperWinningSessionStrategy",
            "bt_start"      : "2022-06-22T08:59:00",
            "bt_end"        : "2023-11-05T08:59:00",
            "markets"       : ['KRW-BTC', 'KRW-ETH', 'KRW-XRP'],
            "cdl_type"      : CandleType.HOUR,
            "vola"          : {"support" : True,
                               "vol_tgt" : 0.04,
                               },
            "timeframe"     : {"support"    : True,
                               "timeframes" : ['08:59', '17:59'],
                               "timegap"    : 1
                               },

            "fixed"         : {"support"     : True,
                               "hdge"        : True,
                               "trade_ratio" : 0.4},

            "stop_loss"     : {"support" : False,
                               "ratio"   : -0.04},
            "trailing_stop" : {"support" : False,
                               "ratio"   : -0.02},
            "take_profit"   : {"support" : False,
                               "ratio"   : 0.07},
            "vars"          : {
                "ma1" : {
                    "func"     : "sma",
                    "params"   : [3],
                    "cdl_type" : CandleType.DAYS_TF,
                    "sources"  : [QItem.close],
                    "unary"    : True
                },
                "ma2" : {
                    "func"     : "sma",
                    "params"   : [5],
                    "cdl_type" : CandleType.DAYS_TF,
                    "sources"  : [QItem.close],
                    "unary"    : True
                },
                "ma3" : {
                    "func"     : "sma",
                    "params"   : [10],
                    "cdl_type" : CandleType.DAYS_TF,
                    "sources"  : [QItem.close],
                    "unary"    : True
                },
                "ma4" : {
                    "func"     : "sma",
                    "params"   : [20],
                    "cdl_type" : CandleType.DAYS_TF,
                    "sources"  : [QItem.close],
                    "unary"    : True
                }
            },
            "buy_systems" : {
                "system1" :
                    {
                        "alias" : "ma1",
                        "left": "price",
                        "op" : ">",
                        "right": "ma1"
                    },
                "system2" :
                    {
                        "alias" : "ma2",
                        "left"  : "price",
                        "op"    : ">",
                        "right" : "ma2"
                    },
                "system3" :
                    {
                        "alias" : "ma3",
                        "left"  : "price",
                        "op"    : ">",
                        "right" : "ma3"
                    },
                "system4" :
                    {
                        "alias" : "ma4",
                        "left"  : "price",
                        "op"    : ">",
                        "right" : "ma4"
                    },
            },
            "buy_system_op" : "system1 and system2 and system3 and system4",
            "sell_systems"   : {
                "system1" :
                    {
                        "alias" : "ma1",
                        "left"  : "price",
                        "op"    : "<",
                        "right" : "ma1"
                    },
                "system2" :
                    {
                        "alias" : "ma2",
                        "left"  : "price",
                        "op"    : "<",
                        "right" : "ma2"
                    },
                "system3" :
                    {
                        "alias" : "ma3",
                        "left"  : "price",
                        "op"    : "<",
                        "right" : "ma3"
                    },
                "system4" :
                    {
                        "alias" : "ma4",
                        "left"  : "price",
                        "op"    : "<",
                        "right" : "ma4"
                    },
            },
            "sell_system_op" : "system1 or system2 or system3 or system4",
        }

        ###################################################################
        strategy_name = "sws_day_hdg_vol_rule"
        environment = Environment(loader = FileSystemLoader("templates/"))
        results_filename = f"{strategy_name}.py"
        results_template = environment.get_template("config_template.jinja2")

        with open(results_filename, mode = "w", encoding = "utf-8") as results :
            results.write(results_template.render(context))
            print(f"... wrote {results_filename}")
        ###################################################################
        results_template = None
        if context["timeframe"]["support"] == True:
            environment = Environment(loader = FileSystemLoader("templates/"))
            results_template = environment.get_template("hdge_stgy_template.jinja2")

        results_filename = f"{context['module_name']}.py"
        with open(results_filename, mode = "w", encoding = "utf-8") as results :
            results.write(results_template.render(context))
            print(f"... wrote {results_filename}")


if __name__ == '__main__' :
    unittest.main()
