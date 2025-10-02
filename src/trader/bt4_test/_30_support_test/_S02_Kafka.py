import unittest

from kafka import KafkaAdminClient
from kafka.admin import NewTopic

import bt4.GlobalProperties as global_prop

class MyTestCase(unittest.TestCase) :
    def test_create_new_channel(self) :
        bootstrap_svr = global_prop.kafka_bootstrap_svr
        quote_pull_req_channel = global_prop.kafka_channel_quote_pull_request
        topic_name = quote_pull_req_channel
        admin_client = KafkaAdminClient(
            bootstrap_servers = bootstrap_svr,
            client_id = 'kafka-python-admin'
        )

        topic_list = admin_client.list_topics()
        print("current topics:")
        for topic in topic_list:
            print(topic)

        # 토픽이 이미 존재하는지 확인
        if topic_name in topic_list :
            print(f"Topic '{topic_name}' already exists. Skipping creation.")
            return

        # 새로운 토픽 생성
        topic = NewTopic(name = topic_name, num_partitions = 1, replication_factor = 1)
        try :
            admin_client.create_topics(new_topics = [topic], validate_only = False)
            print(f"Topic '{topic_name}' created successfully.")
        except TopicAlreadyExistsError :
            print(f"Topic '{topic_name}' already exists. Skipping creation.")
        except Exception as e :
            print(f"Failed to create topic '{topic_name}': {e}")
        finally :
            admin_client.close()

        topic_list = admin_client.list_topics()
        print("current topics:")
        for topic in topic_list:
            print(topic)


if __name__ == '__main__' :
    unittest.main()
