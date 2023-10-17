import sqlite3

con = sqlite3.connect("tutorial.db")
cur = con.cursor()
res = cur.execute("SELECT name FROM sqlite_master")
print(res.fetchone())
print(sqlite3.threadsafety)
