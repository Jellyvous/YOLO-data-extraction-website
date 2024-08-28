import sqlite3

def create_table():
    conn = sqlite3.connect('E:\project\database\detections.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS detections
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 image_name TEXT,
                 detected_class TEXT,
                 detected_text TEXT)''')
    conn.commit()
    conn.close()
    
def show_table():
    conn = sqlite3.connect('E:\project\database\detections.db')
    c = conn.cursor()
    c.execute("SELECT * FROM detections")
    rows = c.fetchall()
    for row in rows:
        print(row)
    conn.close()
    return rows

if __name__ == '__main__':
    show_table()
