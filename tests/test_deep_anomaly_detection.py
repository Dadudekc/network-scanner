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
        self.assertIsNotNone(model)
        self.assertEqual(model.input_shape[1], input_dim)
        self.assertEqual(model.output_shape[1], input_dim)

    @patch('deep_anomaly_detection.train_test_split')
    @patch('deep_anomaly_detection.ModelCheckpoint')
    @patch('deep_anomaly_detection.build_autoencoder')
    def test_train_autoencoder(self, mock_build_autoencoder, mock_checkpoint, mock_train_test_split):
        data = np.random.rand(100, 5)
        mock_train_test_split.return_value = (data[:80], data[80:])
        mock_model = MagicMock()
        mock_build_autoencoder.return_value = mock_model
        mock_model.fit.return_value = None

        model = train_autoencoder(data)

        # Confirm only that fit was called once, then check args
        mock_model.fit.assert_called_once()
        args, kwargs = mock_model.fit.call_args

        # Validate arguments safely using NumPy functions
        np.testing.assert_array_equal(args[0], data[:80])  # x_train
        np.testing.assert_array_equal(args[1], data[:80])  # y_train

        # Validate validation data separately
        np.testing.assert_array_equal(kwargs["validation_data"][0], data[80:])
        np.testing.assert_array_equal(kwargs["validation_data"][1], data[80:])

        # Ensure the remaining kwargs are correct
        self.assertEqual(kwargs["epochs"], 50)
        self.assertEqual(kwargs["batch_size"], 32)
        self.assertEqual(kwargs["callbacks"], [mock_checkpoint.return_value])
        self.assertEqual(kwargs["verbose"], 0)


    def test_detect_anomalies(self):
        """Check anomaly indices rather than MSE."""
        mock_model = MagicMock()
        data = np.random.rand(10, 5)
        mock_reconstructions = data * 0.9
        mock_model.predict.return_value = mock_reconstructions

        anomalies = detect_anomalies(mock_model, data, threshold=0.01)
        mock_model.predict.assert_called_once_with(data)

        # We manually compute the MSE and see which pass threshold
        mse = np.mean(np.power(data - mock_reconstructions, 2), axis=1)
        expected_anomalies = np.where(mse > 0.01)[0]
        np.testing.assert_array_equal(anomalies, expected_anomalies)

    @patch('deep_anomaly_detection.pd.read_csv')
    @patch('deep_anomaly_detection.MinMaxScaler')
    def test_load_preprocess_data(self, mock_scaler, mock_read_csv):
        mock_data = pd.DataFrame(np.random.rand(100, 5))
        mock_read_csv.return_value = mock_data

        mock_scaler_instance = MagicMock()
        transformed_data = np.random.rand(100, 5)
        mock_scaler_instance.fit_transform.return_value = transformed_data
        mock_scaler.return_value = mock_scaler_instance

        data = load_preprocess_data()
        mock_read_csv.assert_called_once_with('your_dataset.csv')
        np.testing.assert_array_equal(
            mock_scaler_instance.fit_transform.call_args[0][0],
            mock_data.values
        )
        np.testing.assert_allclose(data, transformed_data, rtol=1e-5)

    def test_detect_anomalies_with_empty_data(self):
        mock_model = MagicMock()
        empty_data = np.empty((0, 5))
        with self.assertRaises(ValueError):
            detect_anomalies(mock_model, empty_data)

    def test_load_preprocess_data_with_empty_file(self):
        with patch('deep_anomaly_detection.pd.read_csv', return_value=pd.DataFrame()):
            with self.assertRaises(ValueError):
                load_preprocess_data()

    def test_detect_anomalies_with_invalid_shape(self):
        mock_model = MagicMock()
        data = np.random.rand(10, 4)
        with self.assertRaises(ValueError):
            detect_anomalies(mock_model, data)

if __name__ == "__main__":
    unittest.main()
