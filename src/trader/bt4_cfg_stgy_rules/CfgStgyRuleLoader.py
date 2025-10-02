import json

from bt4.Constants import CandleType, QItem
from bt4.resource_path_mgr import RPath


class CfgStgyRuleLoader:
    def __init__(self) :
        pass


    def load(self, cfgstgyrule_path):
        csr_root = RPath.instance().cfgstgyrules_root()
        f = open(f"{csr_root}{cfgstgyrule_path}", encoding = "UTF-8")
        from_json = json.loads(f.read())
        restored_enum = self.restore_enums(from_json)
        f.close()
        return restored_enum


    def restore_enums(self, cfg_rules) :
        cfg_rules["cdl_type"] = CandleType(cfg_rules["cdl_type"])
        for var in cfg_rules["vars"] :
            if isinstance(cfg_rules["vars"][var], dict):
                cfg_rules["vars"][var]["cdl_type"] = CandleType(cfg_rules["vars"][var]["cdl_type"])
                qitems = []
                for src in cfg_rules["vars"][var]["sources"] :
                    # qitems.append(QItem(src))
                    qitems.append(src)
                cfg_rules["vars"][var]["sources"] = qitems

        return cfg_rules