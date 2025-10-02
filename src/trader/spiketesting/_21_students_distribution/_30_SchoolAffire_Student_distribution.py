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

# 함수: calculate_final_max_threshold
def calculate_final_max_threshold(total_capacity, total_students):
    student_to_capacity_ratio = total_students / total_capacity
    final_max_threshold = 1 + (max_assignment_ratio - 1) * student_to_capacity_ratio
    return final_max_threshold

# 함수: assign_priority_students
def assign_priority_students(priority_students, dept_names):
    assigned_students = pd.DataFrame(columns=['student_id', 'dept_assigned', 'score', 'priority_rank'])
    for i, student in priority_students.iterrows():
        dept_choice = student['choice_1']
        score = student['score']
        assigned_students = pd.concat([assigned_students, pd.DataFrame({
            'student_id': [student['student_id']],
            'dept_assigned': [dept_choice],
            'score': [score],
            'priority_rank': [1]
        })], ignore_index=True)
    return assigned_students

# 함수: assign_first_choice
def assign_first_choice(students, dept_names, dept_capacities):
    assigned_students = pd.DataFrame(columns=['student_id', 'dept_assigned', 'score', 'priority_rank'])
    dept_assignments = {dept: [] for dept in dept_names}

    for i, student in students.iterrows():
        dept_choice = student['choice_1']
        score = student['score']
        dept_assignments[dept_choice].append((student['student_id'], score))

    for dept, assignments in dept_assignments.items():
        sorted_assignments = sorted(assignments, key=lambda x: x[1], reverse=True)
        for student_id, score in sorted_assignments:
            assigned_students = pd.concat([assigned_students, pd.DataFrame({
                'student_id': [student_id],
                'dept_assigned': [dept],
                'score': [score],
                'priority_rank': [1]
            })], ignore_index=True)
    return assigned_students

# 함수: generate_student_data
def generate_student_data(student_count, dept_names):
    students = pd.DataFrame({
        'student_id': range(1, student_count + 1),
        'score': [round(random.uniform(50, 100), 2) for _ in range(student_count)]
    })
    for i in range(1, len(dept_names) + 1):
        students[f'choice_{i}'] = np.random.choice(dept_names, student_count, replace=True)
    return students

# 함수: summarize_preference_ratios
def summarize_preference_ratios(assigned_students, dept_names):
    summary = []
    for dept in dept_names:
        dept_students = assigned_students[assigned_students['dept_assigned'] == dept]
        total_assigned = len(dept_students)
        row = {'학과': dept}
        for i in range(1, 12):
            count = len(dept_students[dept_students['priority_rank'] == i]) if i <= 10 else len(dept_students[dept_students['priority_rank'] >= 11])
            ratio = (count / total_assigned) * 100 if total_assigned > 0 else 0
            row[f'{i}순위 배정학생수'] = count
            row[f'배정학생수 대비 {i}순위 배정학생 비율'] = round(ratio, 2)
        summary.append(row)
    return pd.DataFrame(summary)

# 함수: summarize_scores_and_lowest_preference
def summarize_scores_and_lowest_preference(assigned_students, dept_names):
    summary = []
    for dept in dept_names:
        dept_students = assigned_students[assigned_students['dept_assigned'] == dept]
        highest_score = dept_students[dept_students['priority_rank'] == 1]['score'].max()
        lowest_preference = dept_students['priority_rank'].max()
        lowest_score = dept_students[dept_students['priority_rank'] == lowest_preference]['score'].min()
        first_choice_total = len(dept_students[dept_students['priority_rank'] == 1])
        second_choice_total = len(dept_students[dept_students['priority_rank'] <= 2])
        third_choice_total = len(dept_students[dept_students['priority_rank'] <= 3])
        total_students = len(dept_students)

        row = {
            '학과': dept,
            '전체 대상학생 중 1지망 우선순위로 선택한 학생수': first_choice_total,
            '전체 대상학생 중 1지망 우선순위로 선택한 학생비율': round((first_choice_total / total_students) * 100, 2) if total_students > 0 else 0,
            '1지망순위 배정학생 중 최고 점수': highest_score,
            '배정학생 중 최저 지망순위': lowest_preference,
            '배정학생 중 최저 지망순위 중 최저 점수': lowest_score,
            '1지망 합격자 비율(만족도1)': round((first_choice_total / total_students) * 100, 2) if total_students > 0 else 0,
            '1,2지망 합격자 비율(만족도1+2)': round((second_choice_total / total_students) * 100, 2) if total_students > 0 else 0,
            '1,2,3지망 합격자 비율(만족도1+2+3)': round((third_choice_total / total_students) * 100, 2) if total_students > 0 else 0
        }
        summary.append(row)
    return pd.DataFrame(summary)

# 함수: reassign_students
def reassign_students(assigned_students, students, dept_names, dept_capacities, min_assignment, max_assignment):
    reassign_storage = pd.DataFrame(columns=['student_id', 'dept_assigned', 'score', 'priority_rank'] + [f'choice_{i}' for i in range(1, len(dept_names) + 1)])
    dept_assignments = assigned_students.groupby('dept_assigned')

    for dept, group in dept_assignments:
        if len(group) > max_assignment[dept_names.index(dept)]:
            excess_students = group.sort_values(by=['score']).iloc[max_assignment[dept_names.index(dept)]:]
            for _, student in excess_students.iterrows():
                original_student = students[students['student_id'] == student['student_id']].iloc[0]
                student_choices = {f'choice_{i}': original_student[f'choice_{i}'] for i in range(1, len(dept_names) + 1)}
                student_data = {
                    'student_id': student['student_id'],
                    'dept_assigned': student['dept_assigned'],
                    'score': student['score'],
                    'priority_rank': student['priority_rank']
                }
                student_data.update(student_choices)
                reassign_storage = pd.concat([reassign_storage, pd.DataFrame(student_data, index=[0])], ignore_index=True)
                assigned_students = assigned_students[assigned_students['student_id'] != student['student_id']]

    reassign_storage = reassign_storage.sort_values(by=['score'], ascending=False)
    while not reassign_storage.empty:
        print(f"{len(reassign_storage)}: {reassign_storage.head()}")
        for _, student in reassign_storage.iterrows():
            student_choices = [student[f'choice_{i}'] for i in range(1, len(dept_names) + 1)]
            for i in range(2, len(dept_names) + 1):
                next_choice = student.get(f'choice_{i}', None)
                if pd.notna(next_choice):
                    if len(assigned_students[assigned_students['dept_assigned'] == next_choice]) < max_assignment[dept_names.index(next_choice)]:
                        assigned_students = pd.concat([assigned_students, pd.DataFrame({
                            'student_id': [student['student_id']],
                            'dept_assigned': [next_choice],
                            'score': [student['score']],
                            'priority_rank': [i]
                        })], ignore_index=True)
                        reassign_storage = reassign_storage.drop(student.name)
                        break
    return assigned_students

# 함수: adjust_max_and_reassign
def adjust_max_and_reassign(assigned_students, students, dept_names, dept_capacities):
    global min_assignment_ratio, max_assignment_ratio
    reassign_count = 0
    while True:
        summary = summarize_results(assigned_students, dept_names, dept_capacities)
        underfilled_departments = summary[summary['충원율 (%)'] < min_assignment_ratio * 100]
        if underfilled_departments.empty:
            break

        total_deficit = (underfilled_departments['정원'] * min_assignment_ratio - underfilled_departments['배정 학생수']).clip(lower=0).sum()
        total_capacity = sum(dept_capacities)
        deficit_ratio = total_deficit / total_capacity

        max_assignment_ratio = 1 + (max_assignment_ratio - 1 - deficit_ratio)
        max_assignment = [int(cap * max_assignment_ratio) for cap in dept_capacities]
        assigned_students = reassign_students(assigned_students, students, dept_names, dept_capacities, [int(cap * min_assignment_ratio) for cap in dept_capacities], max_assignment)
        reassign_count += 1
        print(f"{reassign_count}차 재배정 완료. 미달학과 충원 중...")

    return assigned_students

# 함수: summarize_results
def summarize_results(assigned_students, dept_names, dept_capacities):
    summary = []
    for dept in dept_names:
        assigned_count = len(assigned_students[assigned_students['dept_assigned'] == dept])
        capacity = dept_capacities[dept_names.index(dept)]
        fill_rate = assigned_count / capacity * 100
        summary.append({
            '학과명': dept,
            '배정 학생수': assigned_count,
            '정원': capacity,
            '충원율 (%)': round(fill_rate, 2)
        })
    return pd.DataFrame(summary)

# 함수: run_assignment_program
def run_assignment_program(dept_file_path, student_count, priority_count, result_file_path):
    global min_assignment_ratio, max_assignment_ratio
    start_time = datetime.now()
    dept_df = pd.read_csv(dept_file_path, header=None)
    dept_names = dept_df.iloc[0].tolist()
    dept_capacities = dept_df.iloc[1].astype(int).tolist()
    total_students = student_count + priority_count
    total_capacity = sum(dept_capacities)
    final_max_threshold = calculate_final_max_threshold(total_capacity, total_students)
    students_df = generate_student_data(student_count + priority_count, dept_names)
    priority_students = students_df.iloc[:priority_count]
    non_priority_students = students_df.iloc[priority_count:]
    assigned_priority = assign_priority_students(priority_students, dept_names)

    print("#### trying assigning first choice...")
    assigned_students_first_df = assign_first_choice(non_priority_students, dept_names, dept_capacities)
    print("#### assigning first choice done!")

    assigned_students_final = pd.concat([assigned_priority, assigned_students_first_df])
    min_assignment = [max(1, int(cap * min_assignment_ratio)) for cap in dept_capacities]
    max_assignment = [int(cap * max_assignment_ratio) for cap in dept_capacities]
    print("#### trying reassigning...")
    assigned_students_final = reassign_students(assigned_students_final, students_df, dept_names, dept_capacities, min_assignment, max_assignment)
    print("#### assigning reassigning done!")

    print("#### trying adjust_max_and_reassign...")
    assigned_students_final = adjust_max_and_reassign(assigned_students_final, students_df, dept_names, dept_capacities)
    print("#### assigning adjust_max_and_reassign done!")
    summary_first = summarize_results(pd.concat([assigned_priority, assigned_students_first_df]), dept_names, dept_capacities)
    summary_final = summarize_results(assigned_students_final, dept_names, dept_capacities)

    ############################################################################################
    ## STKIM added.
    merged_df = pd.merge(assigned_students_final, students_df, on = 'student_id')
    merged_df.to_csv("assignment_sa.csv", encoding = "utf-8-sig")

    dept_df = pd.DataFrame({"학과": dept_names, "모집인원": dept_capacities,"최소": min_assignment, "최대": max_assignment})
    dept_df.to_csv("dept_sa.csv", encoding = "utf-8-sig")
    ############################################################################################

    # 결과 저장
    with pd.ExcelWriter(result_file_path, engine='xlsxwriter') as writer:
        # 첫 번째 시트: 1차 및 최종 배정 결과
        summary_combined = pd.DataFrame({
            '대상학과': dept_names,
            '학생정원': dept_capacities,
            '최초최소값 인원': min_assignment,
            '최초최대값 인원': max_assignment,
            '1단계 배정학생수': summary_first['배정 학생수'],
            '1단계 배정비율 (%)': summary_first['충원율 (%)'],
            '최종 배정학생수': summary_final['배정 학생수'],
            '최종 배정비율 (%)': summary_final['충원율 (%)']
        })
        summary_combined.to_excel(writer, sheet_name='1차 및 최종 배정 결과', index=False)

        # 두 번째 시트: 최종 배정 비율
        pd.DataFrame({
            '대상학생수': [total_students],
            '총정원 대비 대상학생 비율': [total_students / total_capacity],
            '최종최대값': [max_assignment_ratio]
        }).to_excel(writer, sheet_name='최종 배정 비율', index=False)

        # 세 번째 시트: 각 학과별로 배정학생의 지망순위 및 성적 정보
        sorted_students = {dept: [] for dept in dept_names}
        for dept in dept_names:
            dept_students = assigned_students_final[assigned_students_final['dept_assigned'] == dept]
            dept_students = dept_students.sort_values(by=['score'], ascending=False)
            sorted_students[dept] = [f"{row['student_id']}({row['priority_rank']}지망, {row['score']})" for idx, row in dept_students.iterrows()]
        df_sorted_students = pd.DataFrame.from_dict(sorted_students, orient='index').transpose()
        df_sorted_students.to_excel(writer, sheet_name='학생 지망 및 성적', index=False)

        # 네 번째 시트: 0순위로 배정된 학생 정보
        priority_summary = assigned_priority.groupby('dept_assigned').size().reset_index(name='0순위 배정학생 수')
        priority_summary.to_excel(writer, sheet_name='0순위 배정 학생 수', index=False)

        # 다섯 번째 시트: 각 지망순위별 배정 학생 수 및 비율 요약
        preference_ratios = summarize_preference_ratios(assigned_students_final, dept_names)
        preference_ratios.to_excel(writer, sheet_name='지망순위별 배정 비율', index=False)

        # 여섯 번째 시트: 학과별 1순위 최고 점수와 최저 지망순위 배정 점수
        scores_and_lowest_preference = summarize_scores_and_lowest_preference(assigned_students_final, dept_names)
        scores_and_lowest_preference.to_excel(writer, sheet_name='1순위 최고_최저 지망', index=False)

    end_time = datetime.now()
    print(f"프로그램 종료 시각: {end_time.strftime('%H:%M:%S')}")
    elapsed_time = end_time - start_time
    print(f"총 소요 시간: {str(elapsed_time).split('.')[0]}")

# 프로그램 실행
dept_file_path = 'dept.csv'  ## Original
student_count = 856
priority_count = 0           ## make it to zero For Comparison

# dept_file_path = 'dept2.csv'  ## Tailored
# student_count = 1390
# priority_count = 0            ## make it to zero For Comparison

# student_count = int(input("배정할 학생 수를 입력하세요: "))
# priority_count = int(input("0순위 배정 학생 수를 입력하세요: "))
result_file_path = '전공배정결과.xlsx'

run_assignment_program(dept_file_path, student_count, priority_count, result_file_path)
print("Done!")
