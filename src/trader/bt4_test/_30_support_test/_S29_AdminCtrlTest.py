import json
import time
import unittest

from kafka import KafkaProducer

from bt4.Constants import ExType
from bt4.GlobalProperties import kafka_bootstrap_svr, kafka_channel_admin_control
from bt4.common.AdminCtrlReq import ForceEnterLongReq, ForceExitLongReq, RebalanceReq, PauseTradingReq, \
    ResumeTradingReq, StopTradingReq, ForceSettleReq
from bt4.utils.python_utils import load_class_from_module


mingu_uuid = "02e432e9-4321-4b90-85e6-f39d1e17bc72"
stkim_usr_id = "844164d3-207f-4fdf-8464-01a7bf20e663"

class MyTestCase(unittest.TestCase):

    def test_send_force_settle(self):
        producer = KafkaProducer(bootstrap_servers =  kafka_bootstrap_svr)
        _2fsq = ForceSettleReq()
        _2fsq.set_params(mingu_uuid, ExType.upbit.value)
        _2fsq = _2fsq.to_encoded_json()
        producer.send(kafka_channel_admin_control, _2fsq)
        producer.close()

    def test_send_kafka_stop(self):
        producer = KafkaProducer(bootstrap_servers =  kafka_bootstrap_svr)
        _2felq = StopTradingReq()
        _2felq.set_params(mingu_uuid, ExType.upbit.value)
        _2e_felq = _2felq.to_encoded_json()
        producer.send(kafka_channel_admin_control, _2e_felq)
        producer.close()

    def test_send_kafka_resume(self):
        producer = KafkaProducer(bootstrap_servers =  kafka_bootstrap_svr)
        _2felq = ResumeTradingReq()
        _2felq.set_params(mingu_uuid, ExType.upbit.value)
        _2e_felq = _2felq.to_encoded_json()
        producer.send(kafka_channel_admin_control, _2e_felq)
        producer.close()

    def test_send_kafka_pause(self):
        producer = KafkaProducer(bootstrap_servers =  kafka_bootstrap_svr)
        _2felq = PauseTradingReq()
        _2felq.set_params(mingu_uuid, ExType.upbit.value)
        _2e_felq = _2felq.to_encoded_json()
        producer.send(kafka_channel_admin_control, _2e_felq)
        producer.close()

    def test_send_kafka_rebalance(self):
        producer = KafkaProducer(bootstrap_servers =  kafka_bootstrap_svr)
        _2felq = RebalanceReq()
        _2felq.set_params(mingu_uuid, ExType.upbit.value)
        _2e_felq = _2felq.to_encoded_json()
        producer.send(kafka_channel_admin_control, _2e_felq)
        producer.close()

    def test_send_kafka_exit_long(self):
        producer = KafkaProducer(bootstrap_servers =  kafka_bootstrap_svr)

        _2felq = ForceExitLongReq()
        _2felq.set_params(mingu_uuid, ExType.upbit.value, "KRW-XRP", "07:59", "08:59")
        _2e_felq = _2felq.to_encoded_json()
        producer.send(kafka_channel_admin_control, _2e_felq)
        producer.close()

    def test_send_kafka_enter_long(self):
        producer = KafkaProducer(bootstrap_servers =  kafka_bootstrap_svr)

        felq = ForceEnterLongReq()
        # felq.set_params(mingu_uuid, ExType.upbit.value, "KRW-XRP", "08:59")
        felq.set_params(stkim_usr_id, ExType.upbit.value, "KRW-BTC")
        e_felq = felq.to_encoded_json()
        producer.send(kafka_channel_admin_control, e_felq)
        producer.close()

    def test_send_kafka_exit_long_netting(self):
        producer = KafkaProducer(bootstrap_servers =  kafka_bootstrap_svr)

        _2felq = ForceExitLongReq()
        _2felq.set_params(mingu_uuid, ExType.upbit.value, "KRW-XRP")
        _2e_felq = _2felq.to_encoded_json()
        producer.send(kafka_channel_admin_control, _2e_felq)
        producer.close()

    def test_send_kafka_enter_long_netting(self):
        producer = KafkaProducer(bootstrap_servers =  kafka_bootstrap_svr)

        felq = ForceEnterLongReq()
        felq.set_params(mingu_uuid, ExType.upbit.value, "KRW-BTC")
        e_felq = felq.to_encoded_json()
        producer.send(kafka_channel_admin_control, e_felq)
        producer.close()


    def test_send_kafka_exit_long_netting_ft(self):
        producer = KafkaProducer(bootstrap_servers =  kafka_bootstrap_svr)

        _2felq = ForceExitLongReq()
        _2felq.set_params(stkim_usr_id, ExType.upbit.value, "KRW-BTC")
        _2e_felq = _2felq.to_encoded_json()
        producer.send(kafka_channel_admin_control, _2e_felq)
        producer.close()

    def test_send_kafka_enter_long_netting_ft(self):
        producer = KafkaProducer(bootstrap_servers =  kafka_bootstrap_svr)

        felq = ForceEnterLongReq()
        felq.set_params(stkim_usr_id, ExType.upbit.value, "KRW-BTC")
        e_felq = felq.to_encoded_json()
        producer.send(kafka_channel_admin_control, e_felq)
        producer.close()


    def test_marshal_unmarshal_msg(self):
        sender_felq = ForceEnterLongReq()
        sender_felq.set_params('test_account', ExType.upbit.value, '08:20', 'KRW-BTC')
        e_felq = sender_felq.to_encoded_json()
        print(e_felq)

        # sender_felq = ForceExitLongReq()
        # sender_felq.set_params('test', '08:20', '09:20', 'KRW-BTC')
        # e_felq = sender_felq.to_encoded_json()
        # print(e_felq)

        json_message = e_felq.decode()
        a_json = json.loads(json_message)

        admin_req = a_json['admin_req']
        admin_req_obj = load_class_from_module(self.__module__, admin_req)
        admin_req_obj.set_params_with_dict(a_json)
        print(f'{admin_req_obj.__dict__}')


if __name__ == '__main__':
    unittest.main()
