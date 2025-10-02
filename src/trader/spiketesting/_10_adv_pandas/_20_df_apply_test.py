import numpy as np
import pandas as pd

from bt4.utils.python_utils import start_timing, end_n_elapsed_time

rows = 1_000_000
df_students = pd.DataFrame([(f'student_{i}', int(p * 100)) for i, p in enumerate(np.random.rand(rows))], columns=['student', 'score'])
df_students

def apply_grade(score: int):
    if 90 < score <= 100:
        grade = '수'
    elif 80 < score <= 90:
        grade = '우'
    elif 70 < score <= 80:
        grade = '미'
    elif 60 < score <= 70:
        grade = '양'
    else:
        grade = '가'
    return grade

def apply_grade_loop(df: pd.DataFrame):
    list_grade = []
    for i in range(len(df)):
        grade = apply_grade(score=df.iloc[i]['score'])
        list_grade.append(grade)
    df['grade'] = list_grade

def apply_grade_iterrows(df: pd.DataFrame):
    list_grade = []
    for _, row in df.iterrows():
        grade = apply_grade(score=row['score'])
        list_grade.append(grade)
    df['grade'] = list_grade

def apply_grade_itertuples(df: pd.DataFrame):
    list_grade = []
    for row in df.itertuples():
        grade = apply_grade(score=row.score)
        list_grade.append(grade)
    df['grade'] = list_grade

def apply_grade_withapply(df: pd.DataFrame):
    df['grade'] = df.apply(lambda row: apply_grade(score=row['score']), axis=1)


def apply_grade_isin(df: pd.DataFrame) :
    A = df['score'].isin(range(91, 100))
    B = df['score'].isin(range(81, 91))
    C = df['score'].isin(range(71, 81))
    D = df['score'].isin(range(61, 71))
    E = df['score'].isin(range(1, 61))

    df.loc[A, 'grade'] = '수'
    df.loc[B, 'grade'] = '우'
    df.loc[C, 'grade'] = '미'
    df.loc[D, 'grade'] = '양'
    df.loc[E, 'grade'] = '가'

def apply_grade_cut(df: pd.DataFrame):
    df['grade'] = pd.cut(x=df['score'], bins=[1, 60, 70, 80, 90, 100], labels=['가', '양', '미', '우', '수'], include_lowest=True, right=True)

def apply_grade_digitize(df: pd.DataFrame):
    list_grade = np.array(['가', '양', '미', '우', '수'])
    bins = np.digitize(df['score'].values, bins=[60, 70, 80, 90, 100])
    df['grade'] = list_grade[bins]

def apply_grade_numpy(df: pd.DataFrame):
    df["grade"] = np.where((df["score"] > 90) & (df["score"] <= 100), "수",
                           np.where((df["score"] > 80) & (df["score"] <= 90), "우",
                           np.where((df["score"] > 70) & (df["score"] <= 80), "미",
                           np.where((df["score"] > 60) & (df["score"] <= 70), "양",
                           "가"
                          ))))

def apply_grade_numpy_array(df: pd.DataFrame):
    list_grade = []
    for row in df.to_numpy():
        list_grade.append(apply_grade(row[1]))
    df["grade"] = list_grade

level_all_algo = []
for algo in ['loop', 'iterrows', 'itertuples', 'withapply', 'isin', 'cut', 'digitize', 'numpy', 'numpy_array']:
    print(f'[{algo}]')
    cur_time = start_timing()
    globals()[f'apply_grade_{algo}'](df=df_students)
    print(end_n_elapsed_time(cur_time, f'[{algo}]'))
    level_all_algo.append(df_students['grade'].values)