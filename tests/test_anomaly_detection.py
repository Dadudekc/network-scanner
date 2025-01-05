import unittest
import numpy as np
from sklearn.exceptions import NotFittedError
from anomaly_detection import AnomalyDetectionModel


class TestAnomalyDetectionModel(unittest.TestCase):

    def setUp(self):
        # Initialize the model before each test
        self.model = AnomalyDetectionModel()

    def test_model_initialization(self):
        # Test if the model and scaler are properly initialized
        self.assertIsInstance(self.model.model, type(IsolationForest()))
        self.assertIsInstance(self.model.scaler, type(StandardScaler()))

    def test_train_with_valid_data(self):
        # Test training with valid data
        X_train = np.random.rand(50, 3)  # 50 samples, 3 features
        try:
            self.model.train(X_train)
        except Exception as e:
            self.fail(f"Training failed with valid data: {e}")

    def test_predict_with_valid_data(self):
        # Test prediction with valid data after training
        X_train = np.random.rand(50, 3)
        X_test = np.random.rand(10, 3)
        self.model.train(X_train)
        anomalies = self.model.predict(X_test)

        # Ensure predictions return indices (not empty or None)
        self.assertIsInstance(anomalies, np.ndarray)
        self.assertTrue(all(isinstance(i, (int, np.integer)) for i in anomalies))

    def test_predict_before_training(self):
        # Test prediction without training the model
        X_test = np.random.rand(10, 3)
        with self.assertRaises(NotFittedError):
            self.model.predict(X_test)

    def test_train_with_empty_data(self):
        # Test training with empty data
        X_train = np.empty((0, 3))  # Empty dataset with 3 features
        with self.assertRaises(ValueError):
            self.model.train(X_train)

    def test_predict_with_empty_data(self):
        # Test prediction with empty data
        X_train = np.random.rand(50, 3)
        X_test = np.empty((0, 3))  # Empty dataset with 3 features
        self.model.train(X_train)
        with self.assertRaises(ValueError):
            self.model.predict(X_test)

    def test_train_with_incorrect_shape(self):
        # Test training with incorrect feature shape
        X_train = np.random.rand(50, 3)
        X_test = np.random.rand(10, 4)  # Incorrect feature size
        self.model.train(X_train)
        with self.assertRaises(ValueError):
            self.model.predict(X_test)

    def test_predict_with_incorrect_shape(self):
        # Test prediction with data that doesn't match training shape
        X_train = np.random.rand(50, 3)
        X_test = np.random.rand(10, 4)  # Mismatched feature size
        self.model.train(X_train)
        with self.assertRaises(ValueError):
            self.model.predict(X_test)

    def test_anomaly_detection_on_known_data(self):
        # Test anomaly detection on a known dataset
        X_train = np.array([[1, 2], [2, 3], [3, 4], [100, 200]])  # Outlier at [100, 200]
        X_test = np.array([[1.5, 2.5], [101, 201]])  # Outlier test

        self.model.train(X_train)
        anomalies = self.model.predict(X_test)

        # Expect the second sample to be an anomaly
        self.assertIn(1, anomalies)  # Index 1 is the outlier
        self.assertNotIn(0, anomalies)  # Index 0 should not be an anomaly


if __name__ == "__main__":
    unittest.main()
