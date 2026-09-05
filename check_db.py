import sqlite3

conn = sqlite3.connect('db.sqlite3')
c = conn.cursor()
c.execute("SELECT id, app, name FROM django_migrations WHERE app IN ('sites', 'socialaccount')")
rows = c.fetchall()
for r in rows:
    print(r)
conn.close()
