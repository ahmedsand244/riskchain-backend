import sqlite3

def fix():
    try:
        conn = sqlite3.connect('db.sqlite3')
        c = conn.cursor()
        
        # Get socialaccount id
        c.execute("SELECT id FROM django_migrations WHERE app='socialaccount' AND name='0001_initial'")
        row = c.fetchone()
        if not row:
            print("socialaccount.0001_initial not found")
            return
        
        soc_id = row[0]
        
        # We need sites to be before soc_id. Let's update sites to have negative IDs.
        # SQLite allows negative auto-increment IDs.
        c.execute("UPDATE django_migrations SET id = -2 WHERE app='sites' AND name='0001_initial'")
        c.execute("UPDATE django_migrations SET id = -1 WHERE app='sites' AND name='0002_alter_domain_unique'")
        
        conn.commit()
        conn.close()
        print("Migration order fixed successfully.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    fix()
