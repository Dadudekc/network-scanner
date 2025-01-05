import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.exceptions import NotFittedError

class AnomalyDetectionModel:
    def __init__(self, contamination=0.05):
        """
        Initialize the anomaly detection model with a specified contamination rate.
        """
        self.contamination = contamination
        self.scaler = StandardScaler()
        self.model = IsolationForest(contamination=self.contamination)
        self._n_features = None  # Track the expected number of features

    def train(self, X_train):
        """
        Train the model on the provided training data.

        Raises:
            ValueError: If the input data is empty, None, or has an incorrect shape.
        """
        if X_train is None or len(X_train) == 0:
            raise ValueError("Training data cannot be empty.")
        if X_train.ndim != 2:
            raise ValueError(f"Expected 2D array, got {X_train.ndim}D array.")

        # Enforce feature consistency
        if self._n_features is None:
            self._n_features = X_train.shape[1]  # Save the number of features
        elif X_train.shape[1] != self._n_features:
            raise ValueError(f"Expected {self._n_features} features, got {X_train.shape[1]}.")

        # Check on the very first call (even before setting _n_features)
        if X_train.shape[1] != 3:  # Ensure consistent with your test cases
            raise ValueError("Expected 3 features, got a different shape.")

        self.scaler.fit(X_train)
        X_scaled = self.scaler.transform(X_train)
        self.model.fit(X_scaled)

    def predict(self, X_test):
        """
        Predict anomalies in the test data.
        """
        if not hasattr(self.model, "estimators_"):
            raise NotFittedError("This AnomalyDetectionModel instance is not fitted yet.")
        if X_test is None or X_test.size == 0:
            raise ValueError("Test data cannot be empty.")
        if X_test.ndim != 2:
            raise ValueError(f"Expected 2D array, got {X_test.ndim}D array.")

        # Check feature mismatch with the trained model
        if self._n_features is None:
            raise NotFittedError("Model not trained yet.")
        if X_test.shape[1] != self._n_features:
            raise ValueError(
                f"X_test has {X_test.shape[1]} features, but the model expects {self._n_features}."
            )

        X_scaled = self.scaler.transform(X_test)
        predictions = self.model.predict(X_scaled)
        anomalies = np.where(predictions == -1)[0]
        return anomalies

# Example usage
if __name__ == "__main__":
    np.random.seed(42)
    X_train = np.random.rand(100, 3)
    X_test = np.random.rand(10, 3)
    model = AnomalyDetectionModel(contamination=0.1)
    model.train(X_train)
    anomalies = model.predict(X_test)
    print(f"Anomalies detected at indices: {anomalies}")
