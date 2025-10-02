import numpy as np


def select_prediction_length(user_selected_length):
    available_lengths = [3, 6, 12, 24, 36]
    # 사용자가 입력한 길이보다 크거나 같은 가장 작은 예측 길이를 선택
    closest_length = min([length for length in available_lengths if length >= user_selected_length], default=None)

    if closest_length is None:
        raise ValueError("사용자가 입력한 예측 길이에 맞는 모델이 없습니다.")

    return closest_length


def calculate_slope(predictions):
    array = np.array(predictions)
    normalized_array = ((2 * array) - np.max(array) - np.min(array)) / (np.max(array) - np.min(array))
    x_values = range(len(normalized_array))
    slope, _ = np.polyfit(x_values, normalized_array, 1)
    return slope
