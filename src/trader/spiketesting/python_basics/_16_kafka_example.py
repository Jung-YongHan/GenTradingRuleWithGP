from kafka import KafkaAdminClient, KafkaConsumer, KafkaProducer
from kafka.admin import NewTopic
import time
import threading

class Producer(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.stop_event = threading.Event()

    def stop(self):
        print('Producer: stopped!!')
        self.stop_event.set()

    def run(self):
        producer = KafkaProducer(bootstrap_servers='localhost:9092')

        while not self.stop_event.is_set():
            producer.send('auto_trader', b"test")
            producer.send('auto_trader', b"\xc2Hola, mundo!")
            print('Producer: sleep 10 secs')
            time.sleep(10)

        producer.close()


class Consumer(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.stop_event = threading.Event()

    def stop(self):
        print('Consumer: stopped!!')
        self.stop_event.set()

    def run(self):
        consumer = KafkaConsumer(bootstrap_servers='localhost:9092',
                                 auto_offset_reset='latest',
                                 consumer_timeout_ms=1000)
        consumer.subscribe(['auto_trader'])

        while not self.stop_event.is_set():
            print('Consumer: Waiting Event!')
            for message in consumer:
                print('Consumer:', message)
                if self.stop_event.is_set():
                    break

        consumer.close()


def main():
    # Create 'my-topic' Kafka topic
    try:
        admin = KafkaAdminClient(bootstrap_servers='localhost:9092')

        # topic = NewTopic(name='auto_trader',
        #                  num_partitions=1,
        #                  replication_factor=1)
        # admin.create_topics([topic])

    except Exception:
        pass

    tasks = [
        Producer(),
        Consumer()
    ]

    # Start threads of a publisher/producer and a subscriber/consumer to 'my-topic' Kafka topic
    for t in tasks:
        t.start()

    print('MAIN: sleep 100 secs')
    time.sleep(100)

    print('MAIN: request to stop threads...')
    # Stop threads
    for task in tasks:
        task.stop()

    print('MAIN: waiting for other thread\'s termination...')
    for task in tasks:
        task.join()


if __name__ == "__main__":
    main()