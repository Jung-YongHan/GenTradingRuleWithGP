import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

f = open('BTC_USD_2020-04-09_2021-04-08-CoinDesk (1).csv')
coindesk_data = pd.read_csv(f, header=0)
seq = coindesk_data[['Closing Price (USD)', '24h Open (USD)', '24h High (USD)', '24h Low (USD)']].to_numpy()
print('데이터 길이:', len(seq), '\n Front 5 Values\n', seq[0:5])

plt.plot(seq, color='red')
plt.title('Bitcoin Prices (1 Year from 2019-02-28)')
plt.xlabel('Days');
plt.ylabel('Price in USD')
plt.show()
#
#
# ################################################
# ## 시계열 데이터를 윈도우로 자르는 함수
# def seq2dataset(seq, window, horizon):
#     X = [];
#     Y = []
#     for i in range(len(seq) - (window + horizon) + 1):
#         x = seq[i:(i + window)]
#         y = (seq[i + window + horizon - 1])
#         X.append(x)
#         Y.append(y)
#     return np.array(X), np.array(Y)
#
#
# ################################################
# w = 7
# h = 1
# X, Y = seq2dataset(seq, w, h)
#
# print(X.shape, Y.shape)
# print(X[0], Y[0])
#
# print(X[0], Y[0]);
# print(X[-1], Y[-1])
#
# from tensorflow.keras.architecture import Sequential
# from tensorflow.keras.layers import Dense, LSTM, Dropout
#
# split = int(len(X) * 0.7)
# x_train = X[0:split];
# y_train = Y[0:split]
# x_test = X[split:];
# y_test = Y[split:]
#
# ######## Model Building
# model = Sequential()
# model.add(LSTM(units=128, activation='relu', input_shape=x_train[0].shape))
# model.add(Dense(4))
# model.compile(loss='mae', optimizer='adam', metrics=['mae'])
# hist = model.fit(x_train, y_train, epochs=1000, batch_size=1,
#                  validation_data=(x_test, y_test), verbose=2)
#
# ev = model.evaluate(x_test, y_test, verbose=0)
# print("Loss function:", ev[0], "MAE:", ev[1])
#
# pred = model.predict(x_test)
# print('평균절댓값백분율오차(MAPE):', sum(abs(y_test - pred) / y_test / len(x_test)))
#
# #### Accuracy Curve
# plt.plot(hist.history['mae'])
# plt.plot(hist.history['val_mae'])
# plt.title('Model MAE')
# plt.ylabel('MAE')
# plt.xlabel('Epoch')
# plt.legend(['Train', 'Validation'], loc='best')
# plt.grid()
# plt.show()
#
# #### Visualization of Precition
# x_range = range(len(y_test))
# plt.plot(x_range, y_test[x_range], color='red')
# plt.plot(x_range, pred[x_range], color='blue')
# plt.legend(['True Prices', 'Predicted Prices'], loc='best')
# plt.grid()
# plt.show()
#
# #### Focus Specific
# x_range = range(50, 64)
# plt.plot(x_range, y_test[x_range], color='red')
# plt.plot(x_range, pred[x_range], color='blue')
# plt.legend(['True Prices', 'Predicted Prices'], loc='best')
# plt.grid()
# plt.show()
