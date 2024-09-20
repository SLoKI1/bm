import sqlite3

conn = sqlite3.connect('mydatabase.sqlite3')

cursor = conn.cursor()

cursor.execute('''
               CREATE TABLE "users" (
               "id" INTEGER PRIMARY KEY AUTOINCREMENT,
               "id_users" TEXT,
               "fio" TEXT,
               "adress" TEXT,
               "comment" TEXT,
               "product" TEXT
               )''')

conn.commit()
conn.close()