from bt4.ai.models.d_linear import DLinear


class ModelFactory:
    def create_model(self, model_name: str):
        if model_name == "DLinear":
            return DLinear

        else:
            raise ValueError(f"Unknown model type: {model_name}")
