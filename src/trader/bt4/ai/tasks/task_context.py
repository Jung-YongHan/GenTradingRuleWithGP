import pandas as pd

from bt4.ai.args.args_factory import ArgsFactory
from bt4.ai.models.model_factory import ModelFactory
from bt4.ai.tasks.task_strategy import ForecastingTask
from bt4.utils.mylog import init_log

log = init_log()


class AITaskContextCache:
    _cache = {}

    @staticmethod
    def _generate_cache_key(ex_type: str, market: str, model_name: str, task_type: str, **kwargs):
        return (ex_type, market, model_name, task_type, frozenset(kwargs.items()))

    @classmethod
    def get_or_create_context(cls, ex_type: str, market: str, model_name: str, task_type: str, **kwargs):
        cache_key = cls._generate_cache_key(ex_type=ex_type, market=market, model_name=model_name, task_type=task_type, **kwargs)

        if cache_key not in cls._cache:
            context = AITaskContext(ex_type=ex_type, market=market, model_name=model_name, task_type=task_type, **kwargs)
            cls._cache[cache_key] = context

            log.info("Add TaskContext to cache")
        # else:
        #     log.info("Using cached TaskContext instance.")

        return cls._cache[cache_key]


class AITaskContext:
    def __init__(self, ex_type: str, market: str, model_name: str, task_type: str, **kwargs):
        """
        AITaskContext class is responsible for managing the context and execution of AI-based tasks, such as forecasting.
        It initializes the appropriate model and task strategy based on the provided parameters.

        Args:
            ex_type (str): The type of exchange, e.g., 'upbit'.
            market (str): The market identifier, e.g., 'KRW-BTC', 'KRW-ETH'.
            model_name (str): The name of the deep learning model, e.g., 'DLinear'.
            task_type (str): The type of task to be performed, e.g., 'forecasting', 'classification'.

            **kwargs: Additional keyword arguments that can include:
                - candle_type (str): The type of candle data, e.g., 'DAYS'.
                - pred_len (int): The prediction length for forecasting tasks.
                - device (str): The device to run the model on, either 'cpu' or 'cuda'.
                - Any other keyword arguments specific to the model or task.
        """
        self.model_class = ModelFactory().create_model(model_name=model_name)
        self.args = ArgsFactory().create_args(model_name=model_name, task_type=task_type, **kwargs)

        if task_type == "forecasting":
            self.task_strategy = ForecastingTask(ex_type=ex_type, market=market, model_class=self.model_class, args=self.args)

        else:
            raise ValueError(f"Unknown task type: {task_type}")

    def execute(self, market_df: pd.DataFrame):
        return self.task_strategy.perform_task(market_df)
