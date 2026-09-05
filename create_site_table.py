import sqlite3

def fix():
    try:
        conn = sqlite3.connect('db.sqlite3')
        c = conn.cursor()
        
        # Create django_site table exactly as Django expects
        c.execute('''
        CREATE TABLE IF NOT EXISTS "django_site" (
            "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, 
            "domain" varchar(100) NOT NULL UNIQUE, 
            "name" varchar(50) NOT NULL
        )
        ''')
        
        # Insert default site
        c.execute("INSERT OR IGNORE INTO django_site (id, domain, name) VALUES (1, 'localhost', 'Localhost')")
        
        # Mark 0002_alter_domain_unique as faked to avoid altering table issues
        from datetime import datetime
        c.execute("INSERT OR IGNORE INTO django_migrations (app, name, applied) VALUES ('sites', '0002_alter_domain_unique', ?)", (datetime.now(),))
        
        conn.commit()
        conn.close()
        print("Site table created successfully.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    fix()
