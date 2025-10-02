import pandas as pd
import numpy as np
import random
from datetime import datetime

# Python 기본 random 모듈의 시드 고정
random.seed(50)

# numpy 모듈의 시드 고정
np.random.seed(9)

# 전역변수 설정: 최소 및 최대 배정 비율을 정의
min_assignment_ratio = 0.7  # 최소값 70%
max_assignment_ratio = 1.3  # 최대값 130%

allocation = {}

# 함수: calculate_final_max_threshold
def calculate_min_max_threshold(dept_df, total_capacity, total_students):
    global max_assignment_ratio, min_assignment_ratio

    student_to_capacity_ratio = total_students / total_capacity
    final_max_threshold = 1 + (max_assignment_ratio - 1) * student_to_capacity_ratio

    dept_df["최소"] = dept_df["모집인원"] * min_assignment_ratio
    dept_df["최소"] = dept_df["최소"].round(2).astype(int)
    dept_df["최대"] = dept_df["모집인원"] * final_max_threshold
    dept_df["최대"] = dept_df["최대"].round(2).astype(int)

    return dept_df


def generate_student_data(priority_stu_count, orign_stu_count, dept_df, priority_depts):
    dept_names = dept_df["학과"].to_list()
    random_depts = list(set(dept_names) - set(priority_depts))
    total_students_count = priority_stu_count + orign_stu_count
    first_choice = []
    # 1.5배 비율로 1순위 배정
    for idx, dept in enumerate(priority_depts) :
        ## 인기학과는 1.5배 더 많이 생성하고, 융자전/원래전공 비율만큼 인기학과 지원자는 더 많이 생성하게함
        count = int(dept_df.loc[dept_df["학과"] == dept]["모집인원"].item()) * (1.5 + priority_stu_count/orign_stu_count)
        first_choice.extend([dept] * int(count))

    remaining_students = total_students_count - len(first_choice)
    first_choice.extend(np.random.choice(random_depts, remaining_students, replace = True))

    # 나머지 학생들을 섞어서 리스트를 완성
    np.random.shuffle(first_choice)
    first_choice = first_choice[:total_students_count]

    choices = []
    print(len(first_choice))
    print(total_students_count)
    print(first_choice[0])
    print(np.random.choice([dept for dept in dept_names if dept != first_choice[0]], 20, replace = False))

    for i in range(total_students_count) :
        remaining_choices = np.random.choice([dept for dept in dept_names if dept != first_choice[i]], 20,
                                             replace = False)
        choices.append([first_choice[i]] + list(remaining_choices))

    # Convert to DataFrame with columns for each choice from 1st to 21st
    students_df = pd.DataFrame(choices, columns = [f'choice_{i + 1}' for i in range(21)])
    students_df.insert(0, 'student_id', range(1, total_students_count + 1))  # Add student IDs
    students_df["score"] = pd.Series(data = [round(random.uniform(50, 100), 2) for _ in range(total_students_count)],
                                     index = students_df.index)
    return students_df


# 함수: assign_priority_students
def assign_priority_students(students_df, priority_students_df, dept_df):
    for i, student in priority_students_df.iterrows() :
        dept_choice = student['choice_1']
        sid = student["student_id"]
        students_df.loc[students_df["student_id"] == sid, "융자전"] = True
        students_df.loc[students_df["student_id"] == sid, "priority_rank"] = 1
        students_df.loc[students_df["student_id"] == sid, "round"] = "Rnd#1"
        students_df.loc[students_df["student_id"] == sid, "dept_assigned"] = dept_choice

    return students_df

# 함수: assign_first_choice
def exec_1st_round_with_first_choice(non_priority_students_df, students_df, dept_df):
    non_priority_students_df = non_priority_students_df.sort_values(by = "score", ascending = False)

    for i, student in non_priority_students_df.iterrows():
        dept_choice = student['choice_1']
        sid = student["student_id"]
        max_cap_of_dept = dept_df.loc[dept_df["학과"] == dept_choice]["최대"].item()
        if allocation[dept_choice] < max_cap_of_dept:
            students_df.loc[students_df["student_id"] == sid, 'dept_assigned'] = student['choice_1']
            students_df.loc[students_df["student_id"] == sid, 'priority_rank'] = 1
            students_df.loc[students_df["student_id"] == sid, "round"] = "Rnd#2"
            allocation[dept_choice] += 1

    return students_df


# 함수: reassign_students
def exec_2nd_round_with_remaining_choice(students_df, dept_df) :
    not_assigned_students_df = students_df.loc[students_df["dept_assigned"] == "None"].sort_values(by = "score", ascending = False)

    choice_list = [f"choice_{x}" for x in range(2, 22)]

    for _, student in not_assigned_students_df.iterrows() :
        for idx, choice in enumerate(choice_list):
            preferred_dept = student[choice]
            max_cap = dept_df.loc[dept_df["학과"] == preferred_dept]["최대"].item()
            if allocation[preferred_dept] < max_cap :
                sid = student["student_id"]
                students_df.loc[students_df["student_id"] == sid, 'dept_assigned'] = preferred_dept
                students_df.loc[students_df["student_id"] == sid, 'priority_rank'] = idx + 2
                students_df.loc[students_df["student_id"] == sid, "round"] = "Rnd#3"
                allocation[preferred_dept] += 1

    return students_df


def exec_3rd_round_with_filling_min_dept(students_df, dept_df):
    grouped_df = students_df.groupby('dept_assigned')
    absent_dept_names = []
    reassign_candidates_df = pd.DataFrame()
    for dept, student_dept_df in grouped_df :
        # Perform operations on each group here
        sorted_group_df = student_dept_df.loc[student_dept_df["융자전"] == False].sort_values(by = 'score', ascending = False)
        if dept != "None" :
            min_capacity = dept_df.loc[dept_df["학과"] == dept]["최소"].item()
            if len(sorted_group_df) > min_capacity:
                reassign_candidates_df = pd.concat([reassign_candidates_df, sorted_group_df.iloc[min_capacity:]])
            else:
                absent_dept_names.append(dept)

    reassign_candidates_df = reassign_candidates_df.sort_values(by="score", ascending = True) # For all students exceeded minimum limit (70%) of each department and sort ascending order.
    choice_list = [f"choice_{x}" for x in range(1, 22)] # For all choices
    for _, student in reassign_candidates_df.iterrows() :  ## from a student with low scores
        for idx, choice in enumerate(choice_list) :
            prev_assigned_dept = student["dept_assigned"]
            preferred_dept = student[choice]
            min_cap = dept_df.loc[dept_df["학과"] == preferred_dept]["최소"].item()
            alloc = allocation[preferred_dept]
            if alloc < min_cap :
                sid = student["student_id"]
                students_df.loc[students_df["student_id"] == sid, 'dept_assigned'] = preferred_dept
                students_df.loc[students_df["student_id"] == sid, 'priority_rank'] = idx + 1
                students_df.loc[students_df["student_id"] == sid, "round"] = "Rnd#4"
                allocation[preferred_dept] += 1
                allocation[prev_assigned_dept] -= 1
                print(f"reassigning student id {sid} change {prev_assigned_dept} => {preferred_dept}")

    return students_df

def extract_allocation(std_df, dept_df):
    alloc2 = {dept : 0 for dept in dept_df['학과']}
    assigned_df = std_df.groupby('dept_assigned').agg(student_count=('student_id', 'count')).reset_index()
    alloc = {dept : assigned_df.loc[assigned_df["dept_assigned"] ==dept]["student_count"].item() for dept in assigned_df['dept_assigned']}
    alloc2.update(alloc)
    return alloc2

def recalculate_dept_max(students_df, dept_df):

    assigned_dept_df = students_df.groupby('dept_assigned').agg(student_count = ('student_id', 'count')).reset_index()
    assigned_dept_df = assigned_dept_df.rename(columns = {'dept_assigned': "학과"})
    merged_df = pd.merge(dept_df,assigned_dept_df, on = '학과', how = "left")
    merged_df = merged_df.fillna(0)

    merged_df["ass_pcnt"] =merged_df["student_count"] / merged_df["모집인원"]
    # merged_df["최종최대"] = merged_df["최대"]
    popular_dept_df = merged_df.loc[merged_df["ass_pcnt"] >= 0.3].copy()
    popular_dept_df["최대"] = popular_dept_df["모집인원"] + popular_dept_df["student_count"]
    unpopular_dept_df = merged_df.loc[merged_df["ass_pcnt"] < 0.3]
    concat_df = pd.concat([popular_dept_df, unpopular_dept_df])

    merged_df = merged_df.sort_values(by="학과")
    concat_df = concat_df.sort_values(by="학과")
    merged_df["최대"] = concat_df["최대"]
    merged_df["최대"] = merged_df["최대"].round(2).astype(int)

    return merged_df

# 함수: run_assignment_program
def run_assignment_program(dept_file_path, orign_stu_count, priority_stu_count, priority_depts):
    global allocation, min_assignment_ratio, max_assignment_ratio

    start_time = datetime.now()
    dept_df = pd.read_csv(dept_file_path, index_col = 0)

    total_students_count = orign_stu_count + priority_stu_count
    total_capacity = dept_df["모집인원"].sum()

    dept_df = calculate_min_max_threshold(dept_df, total_capacity, total_students_count)

    students_df = generate_student_data(priority_stu_count, orign_stu_count, dept_df, priority_depts)
    priority_students_df = students_df.iloc[:priority_stu_count]
    non_priority_students_df = students_df.iloc[priority_stu_count :]

    ### 1. Data Initialization for distributing students
    students_df["융자전"] = False
    students_df["dept_assigned"] = "None"
    students_df["priority_rank"] = "None"
    students_df["round"] = "None"

    print("#### executing 0 round with priority students ...")
    students_df = assign_priority_students(students_df, priority_students_df, dept_df)
    allocation = extract_allocation(students_df, dept_df)
    dept_df = recalculate_dept_max(students_df, dept_df)
    print("#### executing 0 round done!")

    print("#### executing 1st round with first choice...")
    students_df = exec_1st_round_with_first_choice(non_priority_students_df, students_df, dept_df)
    allocation = extract_allocation(students_df, dept_df)
    print("#### executing 1st round done!")

    print("#### executing 2nd round with remaining choice...")
    students_df = exec_2nd_round_with_remaining_choice(students_df, dept_df)
    allocation = extract_allocation(students_df, dept_df)
    print("#### executing 2nd round done!")

    print("#### executing 3rd round with filling min dept students ...")
    students_df = exec_3rd_round_with_filling_min_dept(students_df, dept_df)
    allocation = extract_allocation(students_df, dept_df)
    print("#### executing 3rd round  done!")

    ############################################################################################
    ## STKIM added.
    student_file_path = "students_sa_eng.csv"
    students_df.to_csv(student_file_path, encoding = "utf-8-sig")
    print(f"Writing students at {student_file_path} done!")

    dept_file_path = "dept_sa_eng.csv"
    dept_df.to_csv(dept_file_path, encoding = "utf-8-sig")
    print(f"Writing department info. at {dept_file_path} done!")
    ############################################################################################


    end_time = datetime.now()
    print(f"프로그램 종료 시각: {end_time.strftime('%H:%M:%S')}")
    elapsed_time = end_time - start_time
    print(f"총 소요 시간: {str(elapsed_time).split('.')[0]}")

# 프로그램 실행
# dept_file_path = 'dept.csv'  ## Original
dept_file_path = "dept_sa.csv"
student_count = 854
priority_count = 60           ## (60)

# dept_file_path = 'dept2.csv'  ## Tailored
# student_count = 1390
# priority_count = 0            ## make it to zero For Comparison

priority_depts = ["Dept1", "Dept2", "Dept3", "Dept4", "Dept5"]

run_assignment_program(dept_file_path, student_count, priority_count, priority_depts)
print("Done!")
