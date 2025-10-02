import json


class AdminCtrlReq:
    KEY_USR_ID = 'usr_id'
    KEY_EX_TYPE = 'ex_type'

    def __init__(self):
        self.admin_req = self.__class__.__name__
        self.usr_id = ''
        self.ex_type = ''

    def set_params_with_dict(self, params):
        self.usr_id  = params[AdminCtrlReq.KEY_USR_ID]
        self.ex_type = params[AdminCtrlReq.KEY_EX_TYPE]

    def set_params(self, account, ex_type):
        self.usr_id = account
        self.ex_type = ex_type

    def to_encoded_json(self):
        obj_dict = self.__dict__
        return json.dumps(obj_dict).encode()

class ForceEnterLongReq(AdminCtrlReq):
    KEY_ENT_LONG_TF = 'ent_long_tf'
    KEY_MARKET      = 'market'

    def __init__(self, params = None):
        super(ForceEnterLongReq, self).__init__()

        if params is not None:
            self.set_params_with_dict(params)
        else:
            self.ent_long_tf = ''
            self.market = ''

    def set_params_with_dict(self, params):
        super(ForceEnterLongReq, self).set_params_with_dict(params)
        self.ent_long_tf = params[ForceEnterLongReq.KEY_ENT_LONG_TF]
        self.market = params[ForceEnterLongReq.KEY_MARKET]

    def set_params(self, account, ex_type, market, ent_long_tf=""):
        super(ForceEnterLongReq, self).set_params(account, ex_type)
        self.ent_long_tf = ent_long_tf
        self.market = market


class ForceExitLongReq(AdminCtrlReq):
    KEY_EXIT_LONG_TF = 'exit_long_tf'
    KEY_MATCHED_ENT_LONG_TF = 'matched_enter_long_tf'
    KEY_MARKET      = 'market'

    def __init__(self, params = None):
        super(ForceExitLongReq, self).__init__()

        if params is not None:
            self.set_params_with_dict(params)
        else:
            self.exit_long_tf = ""
            self.matched_enter_long_tf = ""
            self.market = ""

    def set_params_with_dict(self, params):
        super(ForceExitLongReq, self).set_params_with_dict(params)
        self.exit_long_tf = params[ForceExitLongReq.KEY_EXIT_LONG_TF]
        self.matched_enter_long_tf = params[ForceExitLongReq.KEY_MATCHED_ENT_LONG_TF]
        self.market = params[ForceExitLongReq.KEY_MARKET]

    def set_params(self, account, ex_type, market, exit_long_tf="", matched_enter_long_tf=""):
        super(ForceExitLongReq, self).set_params(account, ex_type)
        self.exit_long_tf = exit_long_tf
        self.matched_enter_long_tf = matched_enter_long_tf
        self.market = market

class ForceSettleReq(AdminCtrlReq):
    def __init__(self, params = None):
        super(ForceSettleReq, self).__init__()
        if params is not None:
            self.set_params_with_dict(params)

class RebalanceReq(AdminCtrlReq):
    def __init__(self, params = None):
        super(RebalanceReq, self).__init__()
        if params is not None:
            self.set_params_with_dict(params)

class PauseTradingReq(AdminCtrlReq):
    def __init__(self, params = None):
        super(PauseTradingReq, self).__init__()
        if params is not None:
            self.set_params_with_dict(params)

class ResumeTradingReq(AdminCtrlReq):
    def __init__(self, params = None):
        super(ResumeTradingReq, self).__init__()
        if params is not None:
            self.set_params_with_dict(params)

class StopTradingReq(AdminCtrlReq):
    def __init__(self, params = None):
        super(StopTradingReq, self).__init__()
        if params is not None:
            self.set_params_with_dict(params)




