
import bt4.utils.mylog as log_module
from bt4.quote.upbit_websocket_quote_dispatcher import start_upbit_quote_service
from bt4.quote.ws_quote_dispatcher import ws_main

log_module.log_mode = 'quote'
log_module.log_mnemonic = 'quote'
log_module.log_strategy = 'quote'

from bt4.utils.mylog import init_log
log = init_log()


if __name__ == '__main__':

    ## upbit
    # start_upbit_quote_service()

    import sys
    ws_main(sys.argv[1 :])

