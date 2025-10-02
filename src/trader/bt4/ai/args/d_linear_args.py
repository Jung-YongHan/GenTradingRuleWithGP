from dataclasses import dataclass

from bt4.ai.args.base_args import BaseArgs, BaseForecastingArgs


@dataclass
class DLinearArgs(BaseArgs):
    moving_avg: int = 25


@dataclass
class DLinearForecastingArgs(DLinearArgs, BaseForecastingArgs):
    c_in: int = 1
    c_out: int = 1

    def __post_init__(self):
        super().__post_init__()


if __name__ == "__main__":
    args = DLinearForecastingArgs(candle_type="DAYS", pred_len=3)
    print(args)
