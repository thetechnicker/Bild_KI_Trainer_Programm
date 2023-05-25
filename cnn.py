import numpy as np
from tensorflow import keras

from PIL import Image

data = {
    "Classes": [
        "1",
        "3"
    ],
    "Images": [
        {
            "label": "Test",
            "File": "C:/Users/lucas/Documents/Python/GUI/Bild_KI_Trainer_Programm/image0.jpg",
            "Yolo": {
                "gx": 0,
                "gy": 0,
                "x": 0,
                "y": 0,
                "h":10,
                "w":10,
                "Class": 0
            }
        }
    ],
    "Yolo":{
        "VerticalGridCount":13,
        "HorizontalGridCount":13
    }
}

# Extract information from data
num_classes = len(data['Classes'])
vgc = data['Yolo']['VerticalGridCount']
hgc = data['Yolo']['HorizontalGridCount']
output_size = 5 + num_classes

# Create x and y datasets
x = []
y = []
for image in data['Images']:
    # Load image data into a numpy array
    #img_data = np.load(image['File'], allow_pickle=True)
    # Open the image file
    img = Image.open(image['File'])

    # Convert the image to a numpy array
    img_data = np.array(img)
    print(f"Input: {img_data}")
    
    x.append(img_data)
    
    # Create yolo output for image
    yolo = image['Yolo']
    gx, gy = yolo['gx'], yolo['gy']
    output = np.zeros((vgc, hgc, output_size))
    output[gy, gx, :5] = [yolo['x'], yolo['y'], yolo["w"], yolo["h"], 1]
    output[gy, gx, 5 + yolo['Class']] = 1
    print(f"Output: {output}")
    y.append(output)

x = np.array(x)
y = np.array(y)

# Define the model
model = keras.models.Sequential()
model.add(keras.layers.Conv2D(32, (3, 3), padding='same', activation='relu', input_shape=x.shape[1:]))
model.add(keras.layers.MaxPooling2D(pool_size=(2, 2)))
model.add(keras.layers.Conv2D(64, (3, 3), padding='same', activation='relu'))
model.add(keras.layers.MaxPooling2D(pool_size=(2, 2)))
model.add(keras.layers.Conv2D(128, (3, 3), padding='same', activation='relu'))
model.add(keras.layers.MaxPooling2D(pool_size=(2, 2)))
model.add(keras.layers.Flatten())
model.add(keras.layers.Dense(256, activation='relu'))
model.add(keras.layers.Dense(vgc * hgc * output_size))
model.add(keras.layers.Reshape((vgc, hgc, output_size)))

# Compile the model
model.compile(optimizer='rmsprop', loss='categorical_crossentropy', metrics=['accuracy'])

# Train the model
model.fit(x, y, epochs=10)

# Save the trained model
model.save('./trained_model.h5')