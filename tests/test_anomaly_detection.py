import unittest
import numpy as np
from sklearn.exceptions import NotFittedError
from anomaly_detection import AnomalyDetectionModel
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

class TestAnomalyDetectionModel(unittest.TestCase):

    def setUp(self):
        # Initialize the model with a fixed contamination rate
        self.model = AnomalyDetectionModel(contamination=0.05)

    def test_model_initialization(self):
        self.assertIsInstance(self.model.model, IsolationForest)
        self.assertIsInstance(self.model.scaler, StandardScaler)

    def test_train_with_valid_data(self):
        X_train = np.random.rand(50, 3)
        try:
            self.model.train(X_train)
        except Exception as e:
            self.fail(f"Training failed with valid data: {e}")

    def test_predict_with_valid_data(self):
        X_train = np.random.rand(50, 3)
        X_test = np.random.rand(10, 3)
        self.model.train(X_train)
        anomalies = self.model.predict(X_test)
        self.assertIsInstance(anomalies, np.ndarray)
        self.assertTrue(all(isinstance(i, (int, np.integer)) for i in anomalies))

    def test_predict_before_training(self):
        X_test = np.random.rand(10, 3)
        with self.assertRaises(NotFittedError):
            self.model.predict(X_test)

    def test_train_with_empty_data(self):
        X_train = np.empty((0, 3))
        with self.assertRaises(ValueError):
            self.model.train(X_train)

    def test_predict_with_empty_data(self):
        X_train = np.random.rand(50, 3)
        X_test = np.empty((0, 3))
        self.model.train(X_train)
        with self.assertRaises(ValueError):
            self.model.predict(X_test)

    def test_train_with_incorrect_shape(self):
        X_train = np.random.rand(50, 3)
        # Suppose user tries to train with 1 feature => mismatch
        incorrect_shape_data = X_train.reshape(-1, 1)
        with self.assertRaises(ValueError) as context:
            self.model.train(incorrect_shape_data)
        self.assertIn("Expected 3 features", str(context.exception))

    def test_predict_with_incorrect_shape(self):
        X_train = np.random.rand(50, 3)
        X_test = np.random.rand(10, 4)  # mismatch
        self.model.train(X_train)
        with self.assertRaises(ValueError) as context:
            self.model.predict(X_test)
        self.assertIn("model expects 3", str(context.exception))

    def test_anomaly_detection_on_known_data(self):
        # Now use 3 features
        np.random.seed(42)
        X_train = np.array([
            [1, 2, 3],
            [2, 3, 4],
            [3, 4, 5],
            [100, 200, 300],  # Clear outlier
        ])
        X_test = np.array([
            [1.5, 2.5, 3.5],
            [101, 201, 301],  # Outlier
        ])

        self.model.train(X_train)
        anomalies = self.model.predict(X_test)
        # Expect index 1 to be an outlier
        self.assertIn(1, anomalies)
        self.assertNotIn(0, anomalies)

    def test_model_state_after_training(self):
        X_train = np.random.rand(50, 3)
        self.model.train(X_train)
        self.assertTrue(hasattr(self.model.scaler, 'mean_'))
        self.assertTrue(hasattr(self.model.model, 'estimators_'))

    def test_predict_on_identical_data(self):
        np.random.seed(42)
        X_train = np.random.rand(50, 3)
        X_test = X_train.copy()
        self.model.train(X_train)
        anomalies = self.model.predict(X_test)
        allowed_anomalies = int(len(X_test) * self.model.contamination)
        self.assertLessEqual(len(anomalies), allowed_anomalies + 1)

    def test_large_datasets(self):
        np.random.seed(42)
        X_train = np.random.rand(10000, 3)
        X_test = np.random.rand(1000, 3)
        self.model.train(X_train)
        anomalies = self.model.predict(X_test)
        self.assertGreaterEqual(len(anomalies), 0)
        self.assertLessEqual(len(anomalies), len(X_test))

if __name__ == "__main__":
    unittest.main()
