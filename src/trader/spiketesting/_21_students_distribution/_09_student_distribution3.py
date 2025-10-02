import pandas as pd
import numpy as np

students_df = pd.read_csv("_2_students.csv", index_col=0)
departments_df = pd.read_csv("departments.csv", index_col = 0)

# Initialize a column for assigned department in students_df
students_df['배정학과'] = None

# Initialize a tracking dictionary for department allocations
allocation = {dept : 0 for dept in departments_df['전공']}
round_remaining = {dept : 0 for dept in departments_df['전공']}

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
            adjusted_students[['번호', '이름', '수능점수', '내신점수', '1학년점수', 'Preference', 'AdjustedScore', '가중Score']])

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



# Mark all students as initially unassigned
students_df['Assigned'] = False
students_df['Round'] = ''

# Round 1: Allocate 40% based on 1st preference
allocate_students_round(students_df, departments_df, ['1순위'], [1.0],0.40, "Rnd#1")

def extract_allocation(std_df):
    assigned_df = std_df.groupby('배정학과').agg(student_count=('번호', 'count')).reset_index()
    alloc = {dept : assigned_df.loc[assigned_df["배정학과"] ==dept]["student_count"].item() for dept in assigned_df['배정학과']}
    return alloc
allocation = extract_allocation(students_df)

# Round 2: Allocate 30% based on 1st, 2nd, 3rd preferences with adjustments
allocate_students_round(students_df, departments_df, ['1순위', '2순위', '3순위'], [1.0, 0.99, 0.98], 0.30, "Rnd#2")
allocation = extract_allocation(students_df)

# Round 3: Allocate 30% based on 1st to 5th preferences with adjustments
allocate_students_round(students_df, departments_df,
                                      ['1순위', '2순위', '3순위', '4순위', '5순위'], [1.0, 0.98, 0.97, 0.96, 0.95], 0.30, "Rnd#3")
allocation = extract_allocation(students_df)

# Round 4: Allocate remaining students to departments with available capacity
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