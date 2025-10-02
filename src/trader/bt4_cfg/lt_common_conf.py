from bt4.Constants import Operation_Type, QUOTE_MODE, ExType, TradeResultStorageType
from bt4.model.storage_mgr import StrategyStorage
from bt4.utils.python_utils import now_dt, dt2str


class LiveTradingCommonConfig:
    def __init__(self):
        pass

    def set_account(self, usr_id, exchange):
        self.usr_id = usr_id
        self.exchange = exchange
        ex_type = ExType[exchange]

        am = StrategyStorage.instance().load_usr_api_key(usr_id, exchange.name)
        print(am)

        if am is None :
            print(f'The system does not contain the keys of the {usr_id} - {exchange}. System will be terminated!')

        self.account_model = am

        exp_dt = self.account_model.exp_date
        remains = exp_dt.replace(tzinfo = None) - now_dt()
        print(f'{usr_id} - {exchange} API remains {remains} days..')
        if now_dt() > exp_dt.replace(tzinfo = None) :
            print(f'{usr_id} - {exchange} API has been expired!! It\'s expiration date is {dt2str(exp_dt)}.')
            input(f"Please update the User {usr_id}'s API Key of {exchange}.")


    def load_params(self, r, params):
        ## Operation Mode
        params[r.OP.OP] = Operation_Type.LIVE_TRADING
        params[r.OP.live.QUOTE_MODE] = QUOTE_MODE.REDIS_KAFKA
        # params[r.OP.live.QUOTE_MODE] = QUOTE_MODE.KAFKA
        # params[r.OP.live.QUOTE_MODE] = QUOTE_MODE.SELF

        params[r.EX.EX_USR_ID] = self.account_model.user_id.__str__()
        params[r.EX.EX_ACCOUNT] = f'{self.usr_id}@{self.exchange.name}'
        params[r.EX.EX_ACCESS_KEY] = self.account_model.access_key
        params[r.EX.EX_SECRET_KEY] = self.account_model.secret_key

        ## File Storage Type
        params[r.RS.RS_TYPE] = TradeResultStorageType.PSQL