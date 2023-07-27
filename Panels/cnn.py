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
            ],
            "Yolo": {
                "VerticalGridCount": 13,
                "HorizontalGridCount": 13
            }
        }
    # Lade modelScript aus einer Datei
    with open('modelScript.txt', 'r') as file:
        modelScript = file.read()
    # Ersetze {data} durch f"{data}"
    modelScript = modelScript.replace('{data}', f'{data}')
    modelScript = modelScript.replace('{ModelStruckture}', f'{ModelStruckture}')
    globals={}
    exec(modelScript, globals)
    print(globals)
