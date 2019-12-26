## Getting started with the Keras Sequential model [[Link]](https://keras.io/getting-started/sequential-model-guide/)

Sequential models just take a linear stack of layers.

```
from keras.models import Sequential
from keras.layers import Dense, Activation

layer_list = [
    	Dense(32, input_shape=(784,)),
    	Activation('relu'),
   		Dense(10)]

model = Sequential(layer_list)

model.add(Activation('softmax'))
```

We can also add layers directly.

Note that the very first layer needs to receive an input shape. This can be done using the `input_shape` argument, a tuple of integers. 3D temporal layers can support the `input_dim` and `input_length` arguments. Specifiying batch size also might be useful for recurrent networks.
	

Once we've set the model's structure, we compile it.
Compilation requires:

1. Optimizer - rmsprop, adagrad, etc.
2. Loss function which the model attempts to minimize.
3. A metric (accuracy or custom metrics can be made)

*In my case, what metrics do I care about?*

```
model.compile(optimizer='rmsprop',
    	loss='categorical_crossentropy',
    	metrics=['accuracy'])
```

We then train the model on Numpy arrays of input data and labels.
Use the `fit()` function to do this (documentation [here](https://keras.io/models/sequential/)).

An example of a sequence classifier with LSTM is given:

```
from keras.models import Sequential
from keras.layers import Dense, Dropout
from keras.layers import Embedding
from keras.layers import LSTM

max_features = 1024

model = Sequential()
model.add(Embedding(max_features, output_dim=256))
model.add(LSTM(128))
model.add(Dropout(0.5))
model.add(Dense(1, activation='sigmoid'))

model.compile(loss='binary_crossentropy',
              optimizer='rmsprop',
              metrics=['accuracy'])

model.fit(x_train, y_train, batch_size=16, epochs=10)
score = model.evaluate(x_test, y_test, batch_size=16)
```

And then a stacked LSTM allows the model to learn higher-level temporal representations.

```
from keras.models import Sequential
from keras.layers import LSTM, Dense
import numpy as np

data_dim = 16
timesteps = 8
num_classes = 10

# expected input data shape: (batch_size, timesteps, data_dim)
model = Sequential()
model.add(LSTM(32, return_sequences=True,
               input_shape=(timesteps, data_dim)))  # returns a sequence of vectors of dimension 32
model.add(LSTM(32, return_sequences=True))  # returns a sequence of vectors of dimension 32
model.add(LSTM(32))  # return a single vector of dimension 32
model.add(Dense(10, activation='softmax'))

model.compile(loss='categorical_crossentropy',
              optimizer='rmsprop',
              metrics=['accuracy'])

# Generate dummy training data
x_train = np.random.random((1000, timesteps, data_dim))
y_train = np.random.random((1000, num_classes))

# Generate dummy validation data
x_val = np.random.random((100, timesteps, data_dim))
y_val = np.random.random((100, num_classes))

model.fit(x_train, y_train,
          batch_size=64, epochs=5,
          validation_data=(x_val, y_val))
```

A final LSTM example is given: one that is stateful. This means that the network keeps internal states from previous batches of samples to use them as initial states when processing the next batch.

Notes done 12/25/2019.

## How to Use Metrics for Deep Learning with Keras in Python [[Link]](https://machinelearningmastery.com/custom-metrics-deep-learning-keras-python/)

Now how would we create custom metrics, and why would they be useful?

*Keras Metrics* - We can choose one or multiple metrics to monitor as we train Keras models, during the `compile()` call. The metrics will be recorded at the end of each epoch on the training dataset, and on the validation set if one was supplied.

*Regression Metrics* - Keras provides:

* Mean squared error
* Mean absolute error
* Mean absolute percentage error
* Cosine proximity

*Classification Metrics* - Keras provides:

* Binary accuracy
* Categorical accuracy
* Sparse categorical accuracy
* Top k categorical accuracy
* Sparse top k categorical accuracy

*Custom Metrics* - One can define their own metrics for Keras to evaluate. Those provided by Keras use exclusively mathematical functions, and any others should use the Keras backend math functions for consistency and speed. Thus in my case custom scale-theory evaluations probably won't be done through Keras.

Done 12/25/2019.

## Keras FAQ: Frequently Asked Keras Questions [[Link]](https://keras.io/getting-started/faq/)

I'm selectively reading this based on a first-pass necessity.

Definitions:

* Sample - An element of a dataset
* Batch - Set of N samples which are processed independently in parallel to then update the model only once (if training). Approximates distribution of data better than pure SGD, but also takes longer to process.
* Epoch - An arbitrary cutoff generally meaning 'one pass over the entire dataset.' In Keras, *callbacks* can be added to run at the end of an epoch.

*Saving models* - Use `model.save(filepath)` to save a Keras model into a HDF5 file, which will contain the model architecture, weights, training config, and state. The model can later be loaded using `load_model`. Commands to save only the architecture, `model.to_json()`, or only the weights, `model.save_weights()`, also exist. Custom layers or functions require some extra work.

*Validation split* - Literally chooses the last x% of the data, without shuffling. Data can be shuffled during training using the `shuffle` argument in `fit()`.

*Stateful RNNs* - This means that the state is saved between batches. All batches must have the same number of samples, and it's assumed that a previous batch contains examples preceding the next batch. Must specify `batch_size`, set `stateful=True` in the RNN layers, and `shuffle=False` when calling `fit()`.

That's the important parts for now.

Last updated 12/25/2019.

## How to use `return_state` or `return_sequences` in Keras [[Link]](https://www.dlology.com/blog/how-to-use-return_state-or-return_sequences-in-keras/)

What do the `return_state` and `return_sequences` parameters mean in Keras?

*Return sequences* - This refers to returning the hidden state, which by default is set to False in Keras. This means that the RNN layer will only return the last hidden state output, which captures some abstract representation of the input sequence. In some cases, this is all we need, e.g. when the last layer is followed by Dense layers to classify or give some score for sentiment analysis.

In other cases, we need the full sequence as output. When this is set to True, the output shape will be (# samples, # time steps, # LSTM units). When False, the shape will be (# samples, # LSTM units).

When you're stacking RNN layers, the former layer(s) should have `return_sequences` as True so that the following layers have the full sequence as input. Also, if you're classifying each time step, as in speech recognition or trigger word detection, set it to True.

*Return states* - In an LSTM, the hidden state and cell state are different. Keras allows you to output the last cell state in addition to the hidden states by setting `return_state=True`. You'd want this when an RNN needs to have its cell state initialized with a previous time step, like in an encoder-decoder model.

This ends the article. Read 12/25/2019.

# To read:
https://adventuresinmachinelearning.com/keras-lstm-tutorial/
https://machinelearningmastery.com/stateful-stateless-lstm-time-series-forecasting-python/
https://keras.io/layers/recurrent/
https://www.tensorflow.org/api_docs/python/tf/keras/layers/LSTM