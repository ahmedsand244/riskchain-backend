import sqlite3

def fix():
    try:
        conn = sqlite3.connect('db.sqlite3')
        c = conn.cursor()
        
        # Delete socialaccount from django_migrations so Django thinks it's not applied
        c.execute("DELETE FROM django_migrations WHERE app='socialaccount'")
        
        conn.commit()
        conn.close()
        print("Cleared socialaccount from migration history.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    fix()
