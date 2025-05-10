import mysql.connector

# Database connection
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'anayed123',
    'database': 'uni_copy'
}

# Connect to database
conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()

# Tables to check
tables = [
    'university',
    'university_type',
    'university_contact',
    'uni_admission_requirements',
    'program',
    'degree',
    'field',
    'financial_aid_and_scholarships',
    'professional_scopes',
    'program_key_module',
    'program_reviews'
]

try:
    for table in tables:
        print(f"\nTable: {table}")
        print("-" * 80)
        cursor.execute(f"DESCRIBE {table}")
        columns = cursor.fetchall()
        for col in columns:
            print(f"Column: {col[0]}")
            print(f"Type: {col[1]}")
            print(f"Null: {col[2]}")
            print(f"Key: {col[3]}")
            print(f"Default: {col[4]}")
            print(f"Extra: {col[5]}")
            print("-" * 40)

except Exception as e:
    print(f"Error: {e}")
finally:
    cursor.close()
    conn.close() 