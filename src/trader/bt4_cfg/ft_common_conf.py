from bt4.Constants import Operation_Type, QUOTE_MODE, ExType, TradeResultStorageType
from bt4.model.storage_mgr import StrategyStorage


class ForwardTestingCommonConfig:
    def __init__(self):
        pass

    def set_account(self, usr_id, exchange):
        self.usr_id = usr_id
        self.exchange = exchange
        ex_type = ExType[exchange]

        am = StrategyStorage.instance().load_usr_api_key(usr_id, exchange.name)
        self.account_model = am
        # if am is not None:
        #     print(f'Given \'{usr_id}\' of \'{ex_type}\' is for trading account, not appropriate for dummy trading. Use another account name.')
        #     input(f"Please check the dummy user id {usr_id}'s API Key of {exchange}. It's redundant.")

    def load_params(self, r, params):
        ## Operation Mode
        params[r.OP.OP] = Operation_Type.FORWARD_TESTING
        params[r.OP.live.QUOTE_MODE] = QUOTE_MODE.REDIS_KAFKA
        # params[r.OP.live.QUOTE_MODE] = QUOTE_MODE.KAFKA
        # params[r.OP.live.QUOTE_MODE] = QUOTE_MODE.SELF

        params[r.EX.EX_USR_ID] = self.usr_id
        params[r.EX.EX_ACCOUNT] = f'{self.usr_id}@{self.exchange.name}'
        params[r.EX.EX_ACCESS_KEY] = ''
        params[r.EX.EX_SECRET_KEY] = ''

        ## File Storage Type
        params[r.RS.RS_TYPE] = TradeResultStorageType.PSQL