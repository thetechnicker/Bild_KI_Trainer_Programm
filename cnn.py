import sqlite3
import numpy as np
from tensorflow import keras

from PIL import Image

def loadData(filename):
    conn = sqlite3.connect(filename)
    c = conn.cursor()

    # Create the tables if they don't exist
    c.execute('''
        CREATE TABLE IF NOT EXISTS classes (
            id INTEGER PRIMARY KEY,
            name TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS neural_nets (
            id INTEGER PRIMARY KEY,
            name TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS images (
            id INTEGER PRIMARY KEY,
            label TEXT,
            file TEXT,
            gx INTEGER,
            gy INTEGER,
            x INTEGER,
            y INTEGER,
            class INTEGER
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS Yolo (
            id INTEGER AUTO_INCREMENT NOT NULL,
            label TEXT,
            value ENUM,
            PRIMARY KEY (id)
        )
    ''')
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


