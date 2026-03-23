import re

with open("main.py", "r", encoding="utf-8") as f:
    content = f.read()

# Replace pymysql imports
content = content.replace("import pymysql", "import psycopg2\nimport psycopg2.extras")

PG_URL = "postgresql://postgres.qjcpaoxhueijqkqjmhph:shaunak43rane@aws-1-ap-southeast-2.pooler.supabase.com:6543/postgres"

# Replace DictCursor connections
content = re.sub(
    r"pymysql\.connect\s*\([^)]+cursorclass=pymysql\.cursors\.DictCursor\s*\)",
    f'psycopg2.connect("{PG_URL}", cursor_factory=psycopg2.extras.DictCursor)',
    content
)

# Replace all standard Cursor connections
content = re.sub(
    r"pymysql\.connect\s*\([^)]+cursorclass=pymysql\.cursors\.Cursor\s*\)",
    f'psycopg2.connect("{PG_URL}")',
    content
)

# Replace any lingering pymysql.connect (if any)
content = re.sub(
    r"pymysql\.connect\s*\([^)]+\)",
    f'psycopg2.connect("{PG_URL}")',
    content
)

# Fix MySQL specific LAST_INSERT_ID() to Postgres equivalent lastval()
content = content.replace("LAST_INSERT_ID()", "lastval()")

# Fix INT AUTO_INCREMENT to SERIAL
content = content.replace("INT AUTO_INCREMENT", "SERIAL")

# Fix ON UPDATE syntax the manual table creation uses
content = content.replace("TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP")

with open("main.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Refactored main.py completed.")
