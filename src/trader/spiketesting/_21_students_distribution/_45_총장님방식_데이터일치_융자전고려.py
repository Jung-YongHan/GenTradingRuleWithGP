import pandas as pd
import numpy as np

students_df = pd.read_csv("students_sa_eng.csv", index_col=0)
departments_df = pd.read_csv("dept_sa_eng.csv", index_col = 0)

def adapt_dataset(students_df, departments_df):
    col_rename_stu_dic1 = {"student_id":"번호", "dept_assigned":"배정학과", "score":"가중Score"}
    col_rename_dic_dept = {}
    for col in students_df.columns:
        if col.startswith("choice_"):
            col_num = col.replace("choice_","")
            col_rename_dic_dept[col] = f"{col_num}순위"
    col_rename_stu_dic1.update(col_rename_dic_dept)

    students_df = students_df.rename(columns = col_rename_stu_dic1)
    students_df = students_df.drop(["priority_rank", "배정학과"], axis = 1)

    departments_df = departments_df.rename(columns = {"학과" : "전공"})
    return students_df, departments_df

students_df, departments_df = adapt_dataset(students_df, departments_df)

################################################################
## 0. Preparing Variables

students_df['배정학과'] = None

allocation = {dept : 0 for dept in departments_df['전공']}
round_remaining = {dept : 0 for dept in departments_df['전공']}

# Mark all students as initially unassigned
students_df['Assigned'] = False
students_df['Round'] = ''

############# Round 0: Allocate Prior Studetns based on 1st preference
def allocate_students_priority(students_df, dept_df, round):
    prior_stu_df = students_df.loc[students_df["융자전"] == True].sort_values(by="가중Score", ascending = False)

    for _, student in prior_stu_df.iterrows():
        pref_dept = student['1순위']
        students_df.loc[students_df['번호'] == student['번호'], '배정학과'] = pref_dept
        allocation[pref_dept] += 1
        # Mark student as assigned, but do not remove them from the DataFrame
        students_df.loc[students_df['번호'] == student['번호'], 'Assigned'] = True
        students_df.loc[students_df['번호'] == student['번호'], 'Round'] = round

    return students_df

def extract_allocation(std_df, dept_df) :
    alloc2 = {dept : 0 for dept in dept_df['전공']}
    assigned_df = std_df.groupby('배정학과').agg(student_count = ('번호', 'count')).reset_index()
    alloc = {dept : assigned_df.loc[assigned_df["배정학과"] == dept]["student_count"].item() for dept in
             assigned_df['배정학과']}
    alloc2.update(alloc)
    return alloc2


def recalculate_dept_max(students_df, dept_df):
    dept_df["ass_pcnt"] =dept_df["student_count"] / dept_df["모집인원"]
    # dept_df["최종최대"] = dept_df["최대"]
    popular_dept_df = dept_df.loc[dept_df["ass_pcnt"] >= 0.3].copy()
    popular_dept_df["최대"] = popular_dept_df["모집인원"] + popular_dept_df["student_count"]
    unpopular_dept_df = dept_df.loc[dept_df["ass_pcnt"] < 0.3]
    concat_df = pd.concat([popular_dept_df, unpopular_dept_df])

    dept_df = dept_df.sort_values(by="전공")
    concat_df = concat_df.sort_values(by="전공")
    dept_df["최대"] = concat_df["최대"]
    dept_df["최대"] = dept_df["최대"].round(2).astype(int)

    return dept_df

students_df = allocate_students_priority(students_df, departments_df, "Rnd#0")
allocation = extract_allocation(students_df, departments_df)
departments_df = recalculate_dept_max(students_df, departments_df)
####################################################################################################
_1st_R_assign = 0.6
_2nd_R_assign = 0.3
_2nd_R_1 = 0.99
_2nd_R_2 = 0.98
_3rd_R_assign = 0.1
_3rd_R_1 = 0.99
_3rd_R_2 = 0.98
_3rd_R_3 = 0.97
_3rd_R_4 = 0.96

# Function to allocate students based on preferences and score adjustments
def allocate_students_round(students_df, departments, preference_columns, score_adjustments, percentage, round) :

    students = students_df[students_df['Assigned'] == False]
    eligible_students = []

    # For each preference in the current round
    for i, pref_col in enumerate(preference_columns) :
        adjusted_students = students.copy()
        adjusted_students['AdjustedScore'] = adjusted_students['가중Score'] * score_adjustments[i]
        adjusted_students['Preference'] = adjusted_students[pref_col]

        # Gather students eligible for this round and preference
        eligible_students.append(
            adjusted_students[['번호', 'Preference', 'AdjustedScore', '가중Score']])

    # Concatenate all eligible students and sort by AdjustedScore
    all_eligible_students = pd.concat(eligible_students).sort_values(by = 'AdjustedScore', ascending = False)\
        # .drop_duplicates(subset = ['번호'])

    max_capacity = {}
    for _, department in departments.iterrows() :
        dept_name = department["전공"]
        assigned_count = allocation[dept_name]
        max_capacity[dept_name] = assigned_count + department['모집인원'] * percentage + round_remaining[dept_name]

    # Assign students to departments based on sorted scores
    for _, student in all_eligible_students.iterrows() :
        preferred_department = student['Preference']
        assigned_count = allocation[preferred_department]

        # Assign student if the department has capacity left
        if assigned_count < int(max_capacity[preferred_department]) and \
                students.loc[students['번호'] == student['번호']]["Assigned"].item() == False:
            students_df.loc[students_df['번호'] == student['번호'], '배정학과'] = preferred_department
            allocation[preferred_department] += 1
            # Mark student as assigned, but do not remove them from the DataFrame
            students_df.loc[students_df['번호'] == student['번호'], 'Assigned'] = True
            students_df.loc[students_df['번호'] == student['번호'], 'Round'] = round

    for _, department in departments.iterrows() :
        dept_name = department["전공"]
        round_remaining[dept_name] = int(max_capacity[dept_name]) - allocation[dept_name]

############# Round 1: Allocate 40% based on 1st preference
allocate_students_round(students_df, departments_df, ['1순위'], [1.0], _1st_R_assign, "Rnd#1")
allocation = extract_allocation(students_df, departments_df)

############# Round 2: Allocate 30% based on 1st, 2nd, 3rd preferences with adjustments
allocate_students_round(students_df, departments_df, ['1순위', '2순위', '3순위'], [1.0, _2nd_R_1, _2nd_R_2], _2nd_R_assign, "Rnd#2")
allocation = extract_allocation(students_df, departments_df)

############# Round 3: Allocate 30% based on 1st to 5th preferences with adjustments
allocate_students_round(students_df, departments_df,
                                      ['1순위', '2순위', '3순위', '4순위', '5순위'], [1.0, _3rd_R_1, _3rd_R_2, _3rd_R_3, _3rd_R_4], _3rd_R_assign, "Rnd#3")
allocation = extract_allocation(students_df, departments_df)

############# Round 4: Allocate remaining students to departments with available capacity
remaining_students = students_df[students_df['Assigned'] == False]


# 가중Score를 고려해 각 학과에 학생을 배정하는 함수
def assign_students_by_department(remained_st_df, students_df, departments_df, round) :
    # 가중Score를 기준으로 학생을 내림차순으로 정렬
    sorted_students = remained_st_df.sort_values(by = "가중Score", ascending = False)

    # 학과별 최소 인원과 최대 인원
    department_min = {dept : departments_df[departments_df["전공"] == dept]["최소"].values[0] for dept in
                      departments_df["전공"]}
    department_max = {dept : departments_df[departments_df["전공"] == dept]["최대"].values[0] for dept in
                      departments_df["전공"]}

    # 1. 먼저 각 학과에 최소 인원을 배정
    for _, student in sorted_students.iterrows() :
        for choice in ["1순위", "2순위", "3순위", "4순위", "5순위", "6순위", "7순위", "8순위", "9순위", "10순위"] :
            preferred_dept = student[choice]

            assigned_count = allocation[preferred_dept]
            if assigned_count < department_min[preferred_dept]:
                students_df.loc[students_df['번호'] == student['번호'], '배정학과'] = preferred_dept
                allocation[preferred_dept] += 1
                # Mark student as assigned, but do not remove them from the DataFrame
                students_df.loc[students_df['번호'] == student['번호'], 'Assigned'] = True
                students_df.loc[students_df['번호'] == student['번호'], 'Round'] = round
                break

    # 2. 남은 학생들을 최대 인원 범위 내에서 배정
    for _, student in sorted_students.iterrows() :
        for choice in ["1순위", "2순위", "3순위", "4순위", "5순위", "6순위", "7순위", "8순위", "9순위", "10순위"] :
            preferred_dept = student[choice]
            assigned_count = allocation[preferred_dept]
            if assigned_count < department_max[preferred_dept] :
                # 최대 인원을 넘지 않는 한도에서 배정
                students_df.loc[students_df['번호'] == student['번호'], '배정학과'] = preferred_dept
                allocation[preferred_dept] += 1
                # Mark student as assigned, but do not remove them from the DataFrame
                students_df.loc[students_df['번호'] == student['번호'], 'Assigned'] = True
                students_df.loc[students_df['번호'] == student['번호'], 'Round'] = round
                break


assign_students_by_department(remaining_students, students_df, departments_df, "Rnd#4")

# Drop the 'Assigned' column before displaying the final DataFrame
# students_df.drop(columns = ['Assigned'], inplace = True)

# Check the number of students assigned and their final allocation
final_df = students_df
final_df_shape = final_df.shape

# Display the first few rows and shape of the final_df
print(final_df)