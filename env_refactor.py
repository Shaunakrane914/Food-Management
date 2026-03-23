with open("main.py", "r", encoding="utf-8") as f:
    content = f.read()

OLD_STR = '"postgresql://postgres.qjcpaoxhueijqkqjmhph:shaunak43rane@aws-1-ap-southeast-2.pooler.supabase.com:6543/postgres"'
NEW_STR = 'os.environ.get("DATABASE_URL")'

if OLD_STR in content:
    # Safely insert dotenv setup where os is imported
    if "from dotenv import load_dotenv" not in content:
        content = content.replace("import os", "import os\nfrom dotenv import load_dotenv\n\nload_dotenv()")
    
    content = content.replace(OLD_STR, NEW_STR)
    
    with open("main.py", "w", encoding="utf-8") as f:
        f.write(content)
    print("main.py secured!")
else:
    print("String not found. Maybe it was already updated?")
