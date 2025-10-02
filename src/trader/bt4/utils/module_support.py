import importlib

class ModuleManager:
    def __init__(self, module_name):
        self.module = importlib.import_module(module_name)

    def get_variable(self, variable_name):
        if hasattr(self.module, variable_name):
            return getattr(self.module, variable_name)
        else:
            raise AttributeError(f"There is no '{variable_name}' in the module '{self.module.__name__}'.")

    def set_variable(self, variable_name, value):
        if hasattr(self.module, variable_name):
            setattr(self.module, variable_name, value)
        else:
            raise AttributeError(f"There is no '{variable_name}' in the module '{self.module.__name__}'.")
