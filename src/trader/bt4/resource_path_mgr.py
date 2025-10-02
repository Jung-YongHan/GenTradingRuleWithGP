from os.path import dirname, join

from bt4 import GlobalProperties
from bt4.utils.python_utils import SingletonInstance
import os

class RPath(SingletonInstance):
    def __init__(self) :
        pass

    def template_root(self):
        root_dir = dirname(dirname(__file__))
        template_root = join(root_dir, f"bt4_cfg{os.sep}template{os.sep}")

        if os.name == 'nt':
            template_root

        return template_root


    def bt_cfg_root_module(self):
        if GlobalProperties.__VERSION__ == "bt3":
            return "bt3_config"
        elif GlobalProperties.__VERSION__ == "bt4":
            return "bt4_cfg"

    def stgy_root(self):
        root_dir = dirname(dirname(__file__))
        stgy_r_module = self.stgy_root_module()

        return join(root_dir, f"{stgy_r_module}{os.sep}")

    def stgy_root_module(self):
        # if os.name == 'nt':
        #     template_root
        if GlobalProperties.__VERSION__ == "bt3":
            return "bulltrader_strategy"
        elif GlobalProperties.__VERSION__ == "bt4":
            return "bt4_stgy_temp"


    def cfgstgyrules_root(self):
        root_dir = dirname(dirname(__file__))
        template_root = join(root_dir, f"bt4_cfg_stgy_rules{os.sep}")

        if os.name == 'nt':
            template_root

        return template_root

