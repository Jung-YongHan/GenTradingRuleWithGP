
import bt4.utils.mylog as log_module
from bt4.utils.bt4_cli_args import get_eqd_argument

log_module.log_mode = 'quote'
log_module.log_mnemonic = 'quote'
log_module.log_strategy = 'quote'

from bt4.utils.mylog import init_log
log = init_log()

from bt4.Constants import QUOTE_MODE
from bt4.quote.ExchangeQuoteDispatcher import ExchangeQuoteDispatcher


def main(args):
    arg_map = get_eqd_argument()
    eql = ExchangeQuoteDispatcher(arg_map["quote_mode"])

    # eql = ExchangeQuoteDispatcher(QUOTE_MODE.REDIS_KAFKA)
    # eql = ExchangeQuoteDispatcher(QUOTE_MODE.KAFKA)
    # eql = ExchangeQuoteDispatcher(QUOTE_MODE.SELF)
    eql.process_quote()

if __name__ == '__main__':
    import sys

    main(sys.argv[1 :])


