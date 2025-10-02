import pandas as pd

pd.set_option('display.max_columns', None)
pd.set_option('display.expand_frame_repr', False)
pd.set_option('max_colwidth', None)

class TradeResultDiffDetail:

    def __init__(self):
        pass

    def compare_detail(self, src_csv_path, target_csv_path):
        src_df = pd.read_csv(src_csv_path, index_col='Unnamed: 0')
        src_df = self.__handle_index__(src_df)
        print(f'Source Rows: {len(src_df)} rows..')

        tgt_df = pd.read_csv(target_csv_path, index_col='Unnamed: 0')
        tgt_df = self.__handle_index__(tgt_df)
        print(f'Target Rows: {len(tgt_df)} rows..')

        diff_df = self.__compare_NaN__(src_df, tgt_df)
        print(f'Diff Rows of Nan: {len(diff_df)} rows..')
        print(diff_df.head(30))

        cols = src_df.columns
        for col in cols:
            if col == 'date':
                continue
            print(f'--'*30)

            src_col_df = src_df[['date', col]]
            tgt_col_df = tgt_df[['date', col]]

            diff_df = src_col_df.merge(tgt_col_df, on='date', indicator=True, how='left')
            print(f'Diff Rows of column \'{src_df.columns}\': {len(diff_df)} rows..')
            print(diff_df.head(30))

    def __handle_index__(self, df):
        # df = df.set_index(['date'])
        df['date'] = pd.to_datetime(df['date'])
        # df.index = pd.to_datetime(df.index)
        # df = df.sort_index()
        return df

    def __compare_NaN__(self, src_df, tgt_df):
        diff_df = src_df.merge(tgt_df, on='date', indicator=True, how='outer').loc[
            lambda x: x['_merge'] != 'both']
        return diff_df



