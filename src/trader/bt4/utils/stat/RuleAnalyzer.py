import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
class RuleAnalyzer:
    def __init__(self):
        pass

    def analyze_rule_contribution2(self, result_file_path) -> dict :
        rslt_df = pd.read_csv(result_file_path, index_col = 'Unnamed: 0', thousands = ',')
        markets = rslt_df["market"].unique().tolist()
        markets.remove("SETT")

        win_sell_df = rslt_df.loc[(rslt_df["market"].isin(markets)) & (rslt_df["order"] == "SELL") & (rslt_df["profit"] > 0)]
        _, win_sell_tai_df = self.__analyze_df__(win_sell_df)
        win_buy_df = rslt_df.loc[rslt_df["id"].isin(win_sell_df["origin_id"])]
        _, win_buy_tai_df = self.__analyze_df__(win_buy_df)

        lose_sell_df = rslt_df.loc[(rslt_df["market"].isin(markets)) & (rslt_df["order"] == "SELL") & (rslt_df["profit"] <= 0)]
        _, lose_sell_tai_df = self.__analyze_df__(lose_sell_df)
        lose_buy_df = rslt_df.loc[rslt_df["id"].isin(lose_sell_df["origin_id"])]
        _, lose_buy_tai_df = self.__analyze_df__(lose_buy_df)

        return win_sell_tai_df, win_buy_tai_df, lose_sell_tai_df, lose_buy_tai_df


    def analyze_ta_support_confidence(self, trade_df, vis_title = "", visualize=False):
        total_num = len(trade_df)
        ti_cols = []
        for col in trade_df.columns :
            if col.startswith("ta_") :
                ti_cols.append(col)

        ti_df = trade_df[ti_cols]
        ta_num_dic = {}
        for idx, col in enumerate(ti_cols) :
            ta = col.replace("ta_", "")
            ta_num = len(ti_df.loc[ti_df[col] == True])
            ta_num_dic[ta] = ta_num

        index_list = []
        supp_list = []
        conf_list = []
        for ix, col in enumerate(ti_cols) :
            ta = col.replace("ta_", "")
            index_list.append(ta)

            supp_row_list = []
            conf_row_list = []
            for ix2, co in enumerate(ti_cols) :
                if ix == ix2 :
                    supp_row_list.append(ta_num_dic[ta] / total_num)
                    if ta_num_dic[ta] == 0:
                        conf_row_list.append(0)
                    else:
                        conf_row_list.append(1)
                else :
                    intersect_two_tas = len(ti_df.loc[(ti_df[col] == True) & (ti_df[co] == True)])
                    supp_row_list.append(intersect_two_tas / total_num)
                    if ta_num_dic[ta] != 0 :
                        conf_row_list.append(intersect_two_tas / ta_num_dic[ta])
                    else:
                        conf_row_list.append(0)

            supp_list.append(supp_row_list)
            conf_list.append(conf_row_list)

        supp_df = pd.DataFrame(supp_list, columns = index_list, index = index_list)
        conf_df = pd.DataFrame(conf_list, columns = index_list, index = index_list)

        if visualize :
            fig = plt.figure(figsize = (8, 3))
            fig.suptitle(vis_title, fontsize = 14)
            ax1 = fig.add_subplot(1, 2, 1)
            s = sns.heatmap(supp_df, annot = True, ax = ax1,
                        cmap = "YlGn", fmt = ".2f")
            s.set(xlabel = 'TA2', ylabel = 'TA1')
            plt.title("Support" + "\n" + "(=TA/ALL, =(TA1 ∩ TA2)/ALL)")

            ax2 = fig.add_subplot(1, 2, 2)
            s2 = sns.heatmap(conf_df, annot = True, ax = ax2,
                        cmap = "YlGn", fmt = ".2f")
            s2.set(xlabel = 'TA2', ylabel = 'TA1')
            plt.title("Confidence" + "\n" + "(=(TA1 ∩ TA2)/TA1)")
            plt.tight_layout()
        return supp_df, conf_df

    def analyze_rule_contribution(self, result_file_path) -> dict :
        rslt_df = pd.read_csv(result_file_path, index_col = 'Unnamed: 0', thousands = ',')
        markets = rslt_df["market"].unique().tolist()

        rslt_dic = {}
        for market in markets:
            if market != "SETT":
                win_sell_df = rslt_df.loc[(rslt_df["market"] == market) & (rslt_df["order"] == "SELL") & (rslt_df["profit"] > 0)]
                print(len(win_sell_df))
                market_win_dic, _ = self.__analyze_df__(win_sell_df)
                rslt_dic[f"{market}_WIN"] = market_win_dic

                win_buy_df = rslt_df.loc[rslt_df["id"].isin(win_sell_df["origin_id"])]
                print(len(win_buy_df))
                market_lose_dic, _ = self.__analyze_df__(win_sell_df)
                rslt_dic[f"{market}_LOSE"] = market_lose_dic
        return rslt_dic

    def __analyze_df__(self, trade_df) :
        ti_df = self.extract_ti_n_usage(trade_df)
        trade_df = pd.concat([trade_df, ti_df], axis = 1)
        market_win_dic = {}
        columns = ti_df.columns
        for idx, col in enumerate(columns) :
            ta = col.replace("ta_", "")
            market_win_dic[ta] = len(ti_df.loc[ti_df[col] == True])
            detail_dic = {}
            for ix, co in enumerate(columns) :
                ta_detail = co.replace("ta_", "")
                if idx == ix :
                    ti_df["and"] = ti_df.sum(axis = 1)
                    detail_dic[ta_detail] = len(ti_df.loc[(ti_df[co] == True) & (ti_df["and"] == 1)])
                else :
                    detail_dic[ta_detail] = len(ti_df.loc[(ti_df[col] == True) & (ti_df[co] == True)])
            market_win_dic[f"{ta}_detail"] = detail_dic
        return market_win_dic, trade_df

    def extract_ti_n_usage(self, trade_df) :
        split_df = trade_df["desc"].str.split("*", expand = True)
        ren_filter = {}
        for col in split_df.columns :
            txt = split_df.head(1)[col].item()
            if (txt is not None) and txt.rfind("[") != -1 :
                ta_name = txt[txt.rfind("[") + 1 :txt.rfind("]")]
                ren_filter[col] = f"ta_{ta_name}"
                split_df[col] = split_df[col].fillna("None")
                split_df[col] = split_df[col].apply(
                    lambda x : True if any(i in x for i in ["True ::"]) else False)

        split_df.rename(columns = ren_filter, inplace=True)
        return split_df[list(ren_filter.values())]


