#!/usr/bin/python

import sqlite3
import os

if os.path.isfile('words.db'):
    os.remove('words.db')

conn = sqlite3.connect('words.db')
print "Opened database successfully";
conn.execute('''CREATE TABLE WORDS
       (id integer primary key autoincrement not null,
        key           text,
        url           text,
        orig_url      text,
        dt            datetime default current_timestamp   );''')

print "Table created successfully";
c = conn.cursor()
with open('bin/normal_words.txt') as f:
    for line in f:
        c.execute("""INSERT INTO WORDS (key) VALUES (?)""", (line.rstrip('\n'),))
f.close()
conn.commit()
print "Records created successfully";
conn.close()

