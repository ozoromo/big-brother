from abc import ABC, abstractmethod

class BaseStrategy(ABC):
    """
    Defines common interface that all face recognition strategies have in
    common.
    """

    @abstractmethod
    def execute(self, training_data, testing_data):
        """
        Executes the strategy.

        Arguments:
        training_data -- List of training data.
        testing_data -- List of test data.

        Return:
        Returns True if the test data matches with the training data and 
        False otherwise.
        """
        pass

    @abstractmethod
    def preprocess_data(self, training_data, testing_data):
        """
        This method converts list of data (mostly images) into correct format 
        for algorithm to work. This method is specifically called on the 
        training data.

        This might be the case if data have another format in one section of 
        the code and therefore need to be converted. You
        may also implement different data processors/converters.

        Arguments:
        training_data -- List with training data. 
        testing_data -- This is one test data.

        Return:
        Tuple with processed data. The first entry being the list of training 
        data and the second entry being the test_data.
        """
        pass
