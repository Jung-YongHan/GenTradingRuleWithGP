
####################################################################################
## Kafka  Property
kafka_bootstrap_svr = 'localhost:9092'        # pc
# kafka_bootstrap_svr = '192.168.1.173:9093'    # dev
# kafka_bootstrap_svr = '192.168.1.21:9092'       # test
# kafka_bootstrap_svr = '141.164.53.64:9093'    # op
kafka_consumer_timeout_ms = 30000
kafka_channel_quote = 'auto_trader'
kafka_channel_admin_control = 'admincontrol'
kafka_channel_strategy_state = 'strategystate'
kafka_channel_quote_pull_request = "quote_pull_request"

is_post_done = False
####################################################################################
## Account
usr_uuid = ''
tid = ''
bt_emergency_stop = False

####################################################################################
## Universal Market Setting
minimum_volumn_krw_limit_for_rebalance = 6000
utility_rate_for_trading = 0.998
# utility_rate_for_trading = 1

####################################################################################
## Live Trading Flag
is_live_trading = False
reset_trades = False

####################################################################################
## BT Version
__VERSION__ = "bt4"

####################################################################################
## redis
# REDIS_HOST = "192.168.1.21"
# REDIS_HOST = 'redis'
# redis_svr = "localhost:6379"              # argument (pc)
redis_svr = "192.168.1.173:6379"         # argument (dev)
# redis_svr = "192.168.1.21:6379"         # argument (test)

REDIS_HOST = redis_svr.split(":")[0]
REDIS_PORT = int(redis_svr.split(":")[1])
REDIS_DB = 0

QUOTE_REDIS_IP_ADDR = REDIS_HOST
####################################################################################
## postgreSQL
postgre_sql_svr =  "192.168.1.173:5432"  # argument (dev)
postgre_sql_db = "bt4"                  # argument (dev)
# postgre_sql_svr =  "192.168.1.21:5432"  # argument (test)
# postgre_sql_db = "bt4"                  # argument


PROJECT_NAME =  "bt4"
DATABASE_URI = postgre_sql_svr.split(":")[0]
DATABASE_PORT = postgre_sql_svr.split(":")[1]
DATABASE_USERNAME = "bulltrader"
DATABASE_PASSWORD = "qnfxmfpdlej12!"

DATABASE_NAME = postgre_sql_db

# DATABASE_NAME = "bt4"
# DATABASE_URI = "localhost"
# DATABASE_URI = "db"

####################################################################################
## Container (Docker / k8s)
CONTAINER_TYPE = "docker"
# CONTAINER_TYPE = "k8s"

CONTAINER_IMAGE_NAME = "rlwns012/qrade:latest"
# CONTAINER_IMAGE_NAME = "rlwns012/qrade:0.0.1"

CONTAINER_NETWORK_NAME = "bt4_trader_default"

CONTAINER_PYTHON_FILE = "./bt4/exec/BullTraderMain.py"

CONTAINER_SERVER_1 = "192.168.1.21"
CONTAINER_SERVER_2 = "192.168.1.173"
CONTAINER_SERVER_3 = "192.168.1.53"

CONTAINER_SERVER_1_USERNAME = "ssel1"
CONTAINER_SERVER_2_USERNAME = "ssel2"
CONTAINER_SERVER_3_USERNAME = "ssel3"

CONTAINER_SERVER_PASSWORD = "dusrntlf512"


####################################################################################
## Enable or Disable Bulk Quote Loader (True => Enable BulkQuoteLoader, Disable LocalQuoteDispatcher)
enable_bulk = True      # argument


####################################################################################
## Trade Request JSon Schema Validation
json_schema_validation_support = True
json_schema_exec_remote = False

ver = "v03"
## local json schema path
main_schema_path = f"../../bt4_json_schema/{ver}/main_schema_local.json"
strategy_schema_path = f"../../bt4_json_schema/{ver}/strategy_schema.json"
vars_schema_path = f"../../bt4_json_schema/{ver}/vars_schema.json"
systems_schema_path = f"../../bt4_json_schema/{ver}/systems_schema.json"

## remote json schema path
main_schema_url = f"http://ssel.asuscomm.com:9080/{ver}/main_schema_remote.json"
vars_schema_url = f"http://ssel.asuscomm.com:9080/{ver}/vars_schema.json"
strategy_schema_url = f"http://ssel.asuscomm.com:9080/{ver}/strategy_schema.json"
systems_schema_url = f"http://ssel.asuscomm.com:9080/{ver}/systems_schema.json"

####################################################################################
## Genetic Algorithm Setting
BASIC_MODE_EXEC_NUM = 100      # 101번 수행
ADV_MODE_EXEC_NUM = 500        # 9 epoch * 50 chromozom + 50 chromozom + 1 = 501번 수행
MAX_MODE_EARLY_STOP_EPOCH = 30 #execution times : 30 * 50 + 50 + 1 = 1551번 이상 수행후 가장 좋을듯한

####################################################################################
## Context Value of Current Quote
cur_quote = None