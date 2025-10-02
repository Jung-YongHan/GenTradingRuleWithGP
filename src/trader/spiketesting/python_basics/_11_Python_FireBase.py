
'''
Follow the directions from the following post to integrate auto_trader and android phone based on the fire base.
https://tre2man.tistory.com/196
'''


import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("auto-trader-95285-firebase-adminsdk-gftpc-4b1f1b8c6d.json")
firebase_admin.initialize_app(cred, {'databaseURL': 'https://auto-trader-95285-default-rtdb.asia-southeast1.firebasedatabase.app/'})

# dir = db.reference()
# dir.update({'자동차': ['기아', '현대', '벤츠']})
#
# dir = db.reference('이동수단/기차')
# dir.update({'1번': 'KTX'})
# dir.update({'2번': '무궁화'})

dir = db.reference()  # 기본 위치 지정
print(dir.get())

dir = db.reference('이동수단/기차/1번')
print(dir.get())

# def getTimeAndHR(self, user, day):
#     data_array = []
#     for key, val in self.ref.child(user).child(day).order_by_key().get().items():
#         data = {"time": key, "HR": val}
#         data_array.append(data)
#     return data_array