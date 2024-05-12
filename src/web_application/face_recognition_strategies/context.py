from face_recognition_strategies.strategies.base_strategy import BaseStrategy

class FaceRecognitionContext:
    def __init__(self, strategy):
        """
        Initializes the strategy.

        Arguments:
        strategy -- The strategy to be set.

        Exceptions:
        ValueError -- Raises exception is the argument doesn't inherit from BaseStrategy.
        """
        self.set_strategy(strategy)

    def set_strategy(self, strategy):
        """
        Set the strategy.

        Arguments:
        strategy -- The strategy to be set.

        Exceptions:
        ValueError -- Raises exception is the argument doesn't inherit from BaseStrategy.
        """
        self._check_is_strategy(strategy)
        self.strategy = strategy

    def _check_is_strategy(self, strategy):
        """
        Checks whether argument inherits fom BaseStrategy and raises exception otherwise.

        Arguments:
        strategy -- Variable to check.

        Exceptions:
        ValueError -- Raises exception is the argument doesn't inherit from BaseStrategy.
        """
        if not issubclass(type(strategy), BaseStrategy):
            raise ValueError(f"Face recognition strategy expected, but '{type(strategy)}' found")

    def execute_strategy(self, training_data, testing_data):
        """
        Executes the strategy that has been set with the given data.
        """
        processed_training_data, processed_testing_data = self.strategy.preprocess_data(
            training_data, testing_data
        )
        return self.strategy.execute(processed_training_data, processed_testing_data)
