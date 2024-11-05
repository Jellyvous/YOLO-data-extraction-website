import sqlite3

def connect_db(db_path='./database/detections.db'):
    conn = sqlite3.connect(db_path)
    return conn

def insert_detection(conn, filename, detected_class, detected_text):
    c = conn.cursor()
    c.execute("INSERT INTO detections (image_name, detected_class, detected_text) VALUES (?, ?, ?)",
              (filename, detected_class, detected_text))
    conn.commit()
