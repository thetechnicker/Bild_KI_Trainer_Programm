import tensorflow as tf

# Define the training data
x = [1, 2, 3, 4]
y = [1, 3, 5, 7]

# Define the model
model = tf.keras.Sequential([tf.keras.layers.Dense(units=1, input_shape=[1])])

# Compile the model
model.compile(optimizer=tf.keras.optimizers.SGD(0.1), loss='mean_squared_error')

# Train the model
model.fit(x, y, epochs=200)

# Make a prediction
print(model.predict([10]))