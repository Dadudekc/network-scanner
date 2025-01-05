import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from keras.models import Model, Sequential
from keras.layers import Input, Dense
from keras.callbacks import ModelCheckpoint

def load_preprocess_data(file_path='your_dataset.csv'):
    data = pd.read_csv(file_path)
    if data.empty or data.shape[1] == 0:
        raise ValueError("Dataset is empty or invalid.")
    scaler = MinMaxScaler()
    scaled_data = scaler.fit_transform(data.values)
    return scaled_data

def build_autoencoder(input_dim, deep=False):
    input_layer = Input(shape=(input_dim,))
    if deep:
        encoded = Dense(128, activation='relu')(input_layer)
        encoded = Dense(64, activation='relu')(encoded)
        decoded = Dense(64, activation='relu')(encoded)
        decoded = Dense(input_dim, activation='sigmoid')(decoded)
        autoencoder = Model(inputs=input_layer, outputs=decoded)
    else:
        encoded = Dense(128, activation='relu')(input_layer)
        encoded = Dense(64, activation='relu')(encoded)
        encoded = Dense(32, activation='relu')(encoded)
        decoded = Dense(64, activation='relu')(encoded)
        decoded = Dense(128, activation='relu')(decoded)
        decoded = Dense(input_dim, activation='sigmoid')(decoded)
        autoencoder = Model(inputs=input_layer, outputs=decoded)

    autoencoder.compile(optimizer='adam', loss='mse')
    return autoencoder


def train_autoencoder(data, deep=False, epochs=50, batch_size=32):
    if data.shape[0] == 0 or data.shape[1] == 0:
        raise ValueError("Input data must not be empty and should have valid dimensions.")
    x_train, x_val = train_test_split(data, test_size=0.2, random_state=42)
    input_dim = data.shape[1]
    autoencoder = build_autoencoder(input_dim, deep=deep)
    checkpoint = ModelCheckpoint('autoencoder.h5', save_best_only=True, verbose=1)

    autoencoder.fit(
        x_train, x_train,
        validation_data=(x_val, x_val),
        epochs=epochs,
        batch_size=batch_size,
        callbacks=[checkpoint],
        verbose=0
    )
    return autoencoder

def detect_anomalies(model, data, threshold=0.01):
    if data.shape[0] == 0 or data.shape[1] == 0:
        raise ValueError("Input data must not be empty and should have valid dimensions.")

    reconstructions = model.predict(data)
    if reconstructions.shape != data.shape:
        raise ValueError(f"Shape mismatch: input {data.shape}, reconstructions {reconstructions.shape}")

    mse = np.mean(np.power(data - reconstructions, 2), axis=1)
    anomalies = np.where(mse > threshold)[0]
    return anomalies
