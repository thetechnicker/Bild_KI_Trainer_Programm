import sqlite3
import numpy as np
from tensorflow import keras

from PIL import Image

def loadData(filename):
    conn = sqlite3.connect(filename)
    c = conn.cursor()
    # Load data from the database
    data = {}
    data['Classes'] = [row[0] for row in c.execute('SELECT name FROM classes')]
    data['Neuronale Netze'] = [row[0] for row in c.execute('SELECT name FROM neural_nets')]
    data['Images'] = []
    for row in c.execute('SELECT label, file, gx, gy, x, y, class FROM images'):
        img_data = {
            'label': row[0],
            'File': row[1],
            'Yolo': {
                'gx': row[2],
                'gy': row[3],
                'x': row[4],
                'y': row[5],
                'Class': row[6]
            }
        }
        data['Images'].append(img_data)

    data["Yolo"]=[]
    for row in c.execute("SELECT label, value FROM Yolo"):
        Yolo={
            row[0]: row[1]
        }
        data["Yolo"].append(Yolo)
    # Close the database connection
    conn.close()
    return data


def createModel(ModelStruckture, data=None):
    if not data:
        data={
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
                        "h": 10,
                        "w": 10,
                        "Class": 0
                    }
                }
            ],
            "Yolo": {
                "VerticalGridCount": 13,
                "HorizontalGridCount": 13
            }
        }
    modelScripts=["from tensorflow.keras.models import Sequential",
        "from tensorflow.keras.layers import Dense, Dropout, Flatten, Conv2D, MaxPooling2D",
        f"data={data}",
        "# Extract information from data",
        "num_classes = len(data['Classes'])",
        "vgc = data['Yolo']['VerticalGridCount']",
        "hgc = data['Yolo']['HorizontalGridCount']",
        "output_size = 5 + num_classes",
        "",
        "# Create x and y datasets",
        "x = []",
        "y = []",
        "for image in data['Images']:",
        "    # Load image data into a numpy array",
        "    #img_data = np.load(image['File'], allow_pickle=True)",
        "    # Open the image file",
        "    img = Image.open(image['File'])",
        "",
        "    # Convert the image to a numpy array",
        "    img_data = np.array(img)",
        "    print(f'Input: {img_data}')",
        "    ",
        "    x.append(img_data)",
        "    ",
        "    # Create yolo output for image",
        "    yolo = image['Yolo']",
        "    gx, gy = yolo['gx'], yolo['gy']",
        "    output = np.zeros((vgc, hgc, output_size))",
        "    output[gy, gx, :5] = [yolo['x'], yolo['y'], yolo['w'], yolo['h'], 1]",
        "    output[gy, gx, 5 + yolo['Class']] = 1",
        "    print(f'Output: {output}')",
        "    y.append(output)",
        "x = np.array(x)",
        "y = np.array(y)",
        f"{ModelStruckture}"]
    seperator="\n"
    modelScript=seperator.join(modelScripts)
    print(modelScript)
    #globals={}
    #exec(modelScript, globals)
    #print(globals)