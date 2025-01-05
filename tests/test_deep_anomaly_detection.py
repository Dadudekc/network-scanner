import unittest
import numpy as np
import pandas as pd
from unittest.mock import patch, MagicMock
from deep_anomaly_detection import (
    load_preprocess_data,
    build_autoencoder,
    train_autoencoder,
    detect_anomalies,
)

class TestDeepAnomalyDetection(unittest.TestCase):

    @patch('deep_anomaly_detection.pd.read_csv')
    @patch('deep_anomaly_detection.MinMaxScaler')
    def test_load_preprocess_data(self, mock_scaler, mock_read_csv):
        # Mock dataset loading
        mock_data = pd.DataFrame(np.random.rand(100, 5))
        mock_read_csv.return_value = mock_data

        # Mock scaler transformation
        mock_scaler_instance = MagicMock()
        mock_scaler_instance.fit_transform.return_value = np.random.rand(100, 5)
        mock_scaler.return_value = mock_scaler_instance

        # Call the function
        data = load_preprocess_data()

        # Assertions
        mock_read_csv.assert_called_once_with('your_dataset.csv')
        mock_scaler_instance.fit_transform.assert_called_once_with(mock_data.values)
        self.assertEqual(data.shape, (100, 5))

    def test_build_autoencoder(self):
        input_dim = 5
        model = build_autoencoder(input_dim)

        # Assertions
        self.assertIsNotNone(model)
        self.assertEqual(model.input_shape[1], input_dim)
        self.assertEqual(model.output_shape[1], input_dim)

    @patch('deep_anomaly_detection.train_test_split')
    @patch('deep_anomaly_detection.ModelCheckpoint')
    @patch('deep_anomaly_detection.build_autoencoder')
    def test_train_autoencoder(self, mock_build_autoencoder, mock_checkpoint, mock_train_test_split):
        # Mock data and splitting
        data = np.random.rand(100, 5)
        mock_train_test_split.return_value = (data[:80], data[80:])
        
        # Mock model
        mock_model = MagicMock()
        mock_build_autoencoder.return_value = mock_model

        # Mock training
        mock_model.fit.return_value = None

        # Call the function
        model = train_autoencoder(data)

        # Assertions
        mock_train_test_split.assert_called_once_with(data, test_size=0.2, random_state=42)
        mock_build_autoencoder.assert_called_once_with(5)
        mock_model.fit.assert_called_once()
        self.assertEqual(model, mock_model)

    @patch('deep_anomaly_detection.Model.predict')
    def test_detect_anomalies(self, mock_predict):
        # Mock model predictions
        mock_model = MagicMock()
        data = np.random.rand(10, 5)
        mock_reconstructions = data - 0.1  # Slightly different data
        mock_predict.return_value = mock_reconstructions

        # Call the function
        mse = detect_anomalies(mock_model, data)

        # Assertions
        mock_model.predict.assert_called_once_with(data)
        self.assertEqual(len(mse), data.shape[0])
        self.assertTrue(np.all(mse >= 0))  # MSE should be non-negative

    @patch('deep_anomaly_detection.load_preprocess_data')
    @patch('deep_anomaly_detection.train_autoencoder')
    @patch('deep_anomaly_detection.detect_anomalies')
    def test_main_execution(self, mock_detect_anomalies, mock_train_autoencoder, mock_load_preprocess_data):
        # Mock function outputs
        mock_data = np.random.rand(100, 5)
        mock_model = MagicMock()
        mock_mse = np.random.rand(100)

        mock_load_preprocess_data.return_value = mock_data
        mock_train_autoencoder.return_value = mock_model
        mock_detect_anomalies.return_value = mock_mse

        # Execute the script
        with patch('builtins.print') as mock_print:
            exec(open("deep_anomaly_detection.py").read())

        # Assertions
        mock_load_preprocess_data.assert_called_once()
        mock_train_autoencoder.assert_called_once_with(mock_data)
        mock_detect_anomalies.assert_called_once_with(mock_model, mock_data)
        mock_print.assert_called_with("Anomaly detection complete.")

if __name__ == "__main__":
    unittest.main()
