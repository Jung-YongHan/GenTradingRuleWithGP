import json
from abc import ABCMeta, abstractmethod

from kafka import KafkaConsumer
import threading
from bt4.utils.mylog import init_log
import bt4.GlobalProperties as global_prop
from bt4.utils.python_utils import now_dt, dt2str

bootstrap_svr       = global_prop.kafka_bootstrap_svr
consumer_timeout    = global_prop.kafka_consumer_timeout_ms
channel             = global_prop.kafka_channel_quote

log = init_log()

# class KafkaProducer(threading.Thread):
#     def __init__(self):
#         threading.Thread.__init__(self)
#         self.stop_event = threading.Event()
#
#     def stop(self):
#         print('Producer: stopped!!')
#         self.stop_event.set()
#
#     def run(self):
#         producer = KafkaProducer(bootstrap_servers=bootstrap_svr)
#
#         while not self.stop_event.is_set():
#             producer.send('auto_trader', b"test")
#             producer.send('auto_trader', b"\xc2Hola, mundo!")
#             print('Producer: sleep 10 secs')
#             time.sleep(10)
#         producer.close()

class KafkaHandler(threading.Thread):
    def __init__(self, channel):
        threading.Thread.__init__(self)
        self.stop_event = threading.Event()
        self.channel = channel

    def stop(self):
        log.debug('Consumer: stopped!!')
        self.stop_event.set()

    def run(self):
        consumer = KafkaConsumer(bootstrap_servers=bootstrap_svr,
                                 auto_offset_reset='latest',
                                 consumer_timeout_ms=consumer_timeout)
        log.info(f'Kafka Consumer has been subscribed in the \'{self.channel}\' channel in ({bootstrap_svr})')
        consumer.subscribe(self.channel)
        while not self.stop_event.is_set():
            # log.debug(f'[{dt2str(now_dt())}] Consumer: Waiting Event in channel {{{self.channel}}}!')
            for message in consumer:
                # log.debug(f'message:{message.topic}')
                # log.debug('Consumer:', message.value.decode())
                self.process_message(message.value)
                if self.stop_event.is_set():
                    break
        consumer.close()

    def process_message(self, message):
        pass


class AdminCtrlListener(metaclass=ABCMeta):
    @abstractmethod
    def ctrl_msg_received(self, msg_json):
        pass

class AdminCtrlMsgReceiver(KafkaHandler):
    def __init__(self, channels):
        super(AdminCtrlMsgReceiver, self).__init__(channels)
        self.listeners = []

    def add_message_listener(self, listener: AdminCtrlListener) -> None:
        self.listeners.append(listener)

    def process_message(self, message):
        # print(f' messages from {message.topic}')
        json_message = message.decode()
        if json_message is not None:
            a_json = json.loads(json_message)
            print(f'## process_message : {a_json}')
            for listener in self.listeners:
                listener.ctrl_msg_received(a_json)
        else:
            print('KAFKA ERROR: No Delivered JSON MESSAGE!!')

