from dataclasses import dataclass, field


@dataclass
class BaseArgs:
    candle_type: str
    device: str


@dataclass
class BaseForecastingArgs(BaseArgs):
    seq_len: int = field(init=False)
    label_len: int = field(init=False)
    pred_len: int
    task_name: str = "forecasting"
    freq: str = field(init=False)

    def __post_init__(self):
        freq_dict = {
            "DAYS": "d",
            "HOUR4": "4h",
            "HOUR": "h",
            "MINUTES_30": "30T",
            "MINUTES_15": "15T",
            "MINUTES_5": "5T",
            "MINUTES_3": "3T",
            "MINUTES_1": "T",
        }
        self.freq = freq_dict[self.candle_type]

        self.seq_len = 48 if self.candle_type == "DAYS" else 96
        self.label_len = self.seq_len // 2
