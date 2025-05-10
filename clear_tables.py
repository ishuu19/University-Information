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

# Tables to clear in order (respecting foreign key constraints)
tables = [
    'program_reviews',
    'program_key_module',
    'professional_scopes',
    'financial_aid_and_scholarships',
    'program',
    'university_contact',
    'uni_admission_requirements',
    'university'
]

try:
    # Disable foreign key checks temporarily
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
    
    # Clear each table
    for table in tables:
        cursor.execute(f"TRUNCATE TABLE {table}")
        print(f"Cleared table: {table}")
    
    # Re-enable foreign key checks
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
    
    # Commit the changes
    conn.commit()
    print("All tables cleared successfully!")

except Exception as e:
    print(f"Error: {e}")
    conn.rollback()
finally:
    cursor.close()
    conn.close() 