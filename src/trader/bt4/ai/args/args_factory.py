from bt4.ai.args.d_linear_args import DLinearForecastingArgs


class ArgsFactory:
    def __init__(self):
        self.arg_strategies = {
            "DLinear": {"forecasting": DLinearForecastingArgs},
        }

    def create_args(self, model_name: str, task_type: str, **kwargs):
        try:
            arg_cls = self.arg_strategies[model_name][task_type](**kwargs)

        except KeyError:
            raise ValueError(f"No strategy found for model '{model_name} or unkown task type: {task_type} '")

        return arg_cls
