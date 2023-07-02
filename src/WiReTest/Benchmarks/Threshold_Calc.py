"""
Calculate an optimal threshold to classify a test face as True ("yes this is the same person as the train pic") or False ("no this is a different person")
Based on distance scores between pictures and the true labels.
In optimizing the threshold many different measures of "how good" a threshold is, are calculated: such as accuracy, recall and precision. More info on those measures here https://towardsdatascience.com/beyond-accuracy-precision-and-recall-3da06bea9f6c
Used in benchmark.py
"""

import numpy as np


class Threshold_Calc:

    def __init__(self, data, labels):
        self.data = data
        self.labels = labels
        self.f_Score_Level = 0
        self.thresh = 0
        self.f_Score = 0

    def add_data_and_labels(self, data, labels):
        # wrong argument type
        if not isinstance(data, np.ndarray) or not isinstance(labels, np.ndarray):
            raise ValueError("The data and labels must be numpy ndarrays for threshold calculation")

        # unintialized self.data and self.labels
        if not isinstance(self.data, np.ndarray) and self.data == None:
            self.data = data
        else:
            # append to already existing data
            self.data = np.append(self.data, data, axis=0)

        if not isinstance(self.labels, np.ndarray) and self.labels == None:
            self.labels = labels
        else:
            self.labels = np.append(self.labels, labels, axis = 0)

    def get_num_tp(self, threshold: float, data = None, labels = None) -> int:
        """
        Number of true positives: points that the model would've predicated as true (under threshold) that have the actual label true
        """
        if not isinstance(data, np.ndarray) or not isinstance(labels, np.ndarray):
            data = self.data
            labels = self.labels

        under_threshold = (data <= threshold)
        bool_arr = np.logical_and(under_threshold, labels)
        return np.sum(bool_arr)

    def get_num_tn(self, threshold: float, data = None, labels = None) -> int:
        """
        Number of true negatives: points that the model would've predicated as false (over threshold) that have the actual label false
        """
        if not isinstance(data, np.ndarray) or not isinstance(labels, np.ndarray):
            data = self.data
            labels = self.labels

        over_threshold = (data > threshold)
        bool_arr = np.logical_and(over_threshold, np.invert(labels))
        return np.sum(bool_arr)

    def get_num_fp(self, threshold: float, data = None,  labels = None) -> int:
        """
        Number of false positives: points that the model would've predicated as true (under threshold) that have the actual label false
        """
        if not isinstance(data, np.ndarray) or not isinstance(labels, np.ndarray):
            data = self.data
            labels = self.labels
        under_threshold = (data <= threshold)
        bool_arr = np.logical_and(under_threshold, np.invert(labels))
        return np.sum(bool_arr)

    def get_num_fn(self, threshold: float, data = None, labels = None) -> int:
        """
        Number of false negatives: points that the model would've predicated as false (over threshold) that have the actual label true
        """
        if not isinstance(data, np.ndarray) or not isinstance(labels, np.ndarray):
            data = self.data
            labels = self.labels

        over_threshold = (data > threshold)
        bool_arr = np.logical_and(over_threshold, labels)
        return np.sum(bool_arr)

    def calc_recall(self, threshold: float, data = None, labels = None) -> float:
        """
        Calculates the recall for a given threshold. Recall is "a models ability to find all datapoints of interest": 
        true positives / (true positives + false negatives)
        """
        if not isinstance(data, np.ndarray) or not isinstance(labels, np.ndarray):
            data = self.data
            labels = self.labels

        tp = self.get_num_tp(threshold, data = data, labels = labels)
        fn = self.get_num_fn(threshold, data = data, labels = labels)
        return tp / (tp + fn)


    def calc_precision(self, threshold: float, data = None, labels = None) -> float:
        """
        Calculates precision for a given threshold. Precision is proportion of true positives in all the points that the model says are positive: 
        true positives / (true positives + false positives)
        """
        if not isinstance(data, np.ndarray) or not isinstance(labels, np.ndarray):
            data = self.data
            labels = self.labels

        tp = self.get_num_tp(threshold, data = data, labels = labels)
        fp = self.get_num_fp(threshold, data = data, labels = labels)
        #print(tp)
        #print(fp)
    
        return tp / (tp + fp)

    def calc_f_score(self, threshold: float, f_score_level=1, data = None, labels = None) -> float:
        """
        Measure of the models accuracy: https://towardsdatascience.com/beyond-accuracy-precision-and-recall-3da06bea9f6c and https://en.wikipedia.org/wiki/F-score
        """
        if not isinstance(data, np.ndarray) or not isinstance(labels, np.ndarray):
            data = self.data
            labels = self.labels

        #formula from wikipedia
        beta_sqr = f_score_level**2
        prec = self.calc_precision(threshold, data = data, labels =labels)
        rec = self.calc_recall(threshold, data = data, labels = labels)
        score = (1 + beta_sqr) * ((prec * rec) / ((beta_sqr * prec) + rec))
        return score

    def calc_threshold_range(self, min_threshold = 0, max_threshold = 0, step_num = 10, data = None) -> list:
        """
        Generates a list of thresholds bbetween [min_threshold, max_threshold] with {steps_num} steps between them. 
        If no values are given, the min. and max. are calculated based on data in self.data
        """
        if not isinstance(data, np.ndarray):
            data = self.data

        if min_threshold == 0:
            min_threshold = np.min(data)

        if max_threshold == 0:
            max_threshold = np.max(data)

        return np.linspace(min_threshold, max_threshold, step_num)

    def threshold_with_max_f_score(self, tested_thresholds: list, f_score_level=1, data = None, labels = None):
        """
        Find the threshold that has the lowest f-score (at given f-score level). Tests all thresholds in the given list
        """
        if not isinstance(data, np.ndarray) or not isinstance(labels, np.ndarray):
            data = self.data
            labels = self.labels

        f_scores = np.zeros((len(tested_thresholds),))

        for i, threshold in enumerate(tested_thresholds):
            f_scores[i] = self.calc_f_score(
                    threshold, 
                    f_score_level=f_score_level, 
                    data=data, 
                    labels=labels
                )

        max_f_score = np.max(f_scores)
        calc_threshold = tested_thresholds[np.argmax(f_scores)]

        return calc_threshold, max_f_score

    def set_thres_range(self, min_threshold = 0, max_threshold = 0, step_num = 10, data = None):
        """
        Allows for user defined range of thresholds that should be tested, out of which the optimum is picked
        """
        self.threshold_range = self.calc_threshold_range(
                min_threshold=min_threshold, 
                max_threshold=max_threshold, 
                step_num=step_num, 
                data=data
            )

    def get_thres_range(self):
        # check if self.threshold_range is initialized
        if not isinstance(getattr(self, "threshold_range", False), np.ndarray):
            # uninitialized so we generate a default
            self.set_thres_range()
        return self.threshold_range

    def calc_and_print_results(self, f_score_level, data = None, labels = None):
        """
        Combines all functions and prints results to the console
        """
        if not isinstance(data, np.ndarray) or not isinstance(labels, np.ndarray):
            data = self.data
            labels = self.labels

        print(data, labels)
        tested_thresholds = self.get_thres_range()
        thres, f_score = self.threshold_with_max_f_score(
                tested_thresholds, 
                f_score_level=f_score_level, 
                data=data, 
                labels=labels
            )
        print(f"Calculated optimal threshold with maximum f_{f_score_level}-score is: {thres} and has a f-score of {f_score}")
        print()

        self.f_Score_Level = f_score_level
        self.thresh = thres
        self.f_Score = f_score
        true_pos = self.get_num_tp(thres, data = data, labels = labels)
        true_neg = self.get_num_tn(thres, data = data, labels = labels)
        false_pos = self.get_num_fp(thres, data = data, labels = labels)
        false_neg = self.get_num_fn(thres, data = data, labels = labels)
        print(f"At that threshold there are {true_pos} true positives, {true_neg} true negatives, {false_pos} False Positives and {false_neg} False Negatives")
        print()
        print("csv format: <f-score-level,threshold,f-score,tp,tn,fp,fn,recall,precision>")
        print(f'{f_score_level},{thres},{f_score},{true_pos},{true_neg},{false_pos},{false_neg},{self.calc_recall(thres,data,labels)},{self.calc_precision(thres,data,labels)}')

