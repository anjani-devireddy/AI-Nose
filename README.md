# AI Artificial Nose

An embedded **AI-powered artificial nose** that uses a **Grove Multichannel Gas Sensor V2**, **Seeed Wio Terminal**, and **Edge Impulse** to identify substances from their gas-response patterns.

## How It Works

```text
Gas Sensor
    ↓
4 Gas Channels
    ↓
Spectral Analysis
    ↓
Machine Learning Model
    ↓
Substance Prediction
```

The trained model runs directly on the Wio Terminal, enabling **real-time, offline inference**.

## Technology Stack

* Seeed Wio Terminal
* Grove Multichannel Gas Sensor V2
* Edge Impulse
* TinyML / Neural Networks
* Arduino / C++
* Python

## Current Features

* Four-channel gas sensing
* Edge Impulse-based classification
* On-device inference
* Confidence-based prediction
* Real-time results on the Wio Terminal display
* Button-controlled new predictions

## Project Status

The prototype successfully performs gas sensing and on-device classification. The next phase focuses on expanding the training dataset, improving multi-substance recognition, and building the final demonstration enclosure.
