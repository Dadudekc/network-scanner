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
        mock_model = MagicMock()
        data = np.random.rand(10, 5)
        mock_reconstructions = data * 0.9
        mock_predict.return_value = mock_reconstructions

        # Call the function
        mse = detect_anomalies(mock_model, data)

        # Assertions
        self.assertEqual(len(mse), data.shape[0])
        self.assertTrue(np.all(mse >= 0))

    @patch('deep_anomaly_detection.pd.read_csv')
    @patch('deep_anomaly_detection.MinMaxScaler')
    def test_load_preprocess_data(self, mock_scaler, mock_read_csv):
        mock_data = pd.DataFrame(np.random.rand(100, 5))
        mock_read_csv.return_value = mock_data

        mock_scaler_instance = MagicMock()
        transformed_data = np.random.rand(100, 5)
        mock_scaler_instance.fit_transform.return_value = transformed_data
        mock_scaler.return_value = mock_scaler_instance

        # Call the function
        data = load_preprocess_data()

        # Assertions
        np.testing.assert_array_almost_equal(data, transformed_data)


if __name__ == "__main__":
    unittest.main()
