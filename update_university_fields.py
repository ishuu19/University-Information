import mysql.connector
import random
from faker import Faker

# Initialize Faker
fake = Faker()

# Database connection
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'anayed123',
    'database': 'universityadmissiondb'
}

# Connect to database
conn = mysql.connector.connect(**db_config)
cursor = conn.cursor(buffered=True)

def generate_student_org_description():
    orgs = [
        "Student Government",
        "Cultural Clubs",
        "Academic Societies",
        "Sports Teams",
        "Music Groups",
        "Environmental Club",
        "Tech Club",
        "Business Club",
        "Service Groups",
        "International Club"
    ]
    selected_orgs = random.sample(orgs, random.randint(3, 5))
    return f"Active campus with {random.randint(30, 100)} student organizations including {', '.join(selected_orgs)}."

def generate_athletics_description():
    sports = [
        "Basketball",
        "Football",
        "Soccer",
        "Tennis",
        "Swimming",
        "Track",
        "Volleyball",
        "Baseball",
        "Golf",
        "Rowing"
    ]
    selected_sports = random.sample(sports, random.randint(3, 5))
    return f"Strong athletic program with {random.randint(10, 20)} varsity teams including {', '.join(selected_sports)}."

def update_university_fields():
    try:
        # Get total number of universities
        cursor.execute("SELECT COUNT(*) FROM university")
        total_universities = cursor.fetchone()[0]
        print(f"Found {total_universities} universities to update")

        # Get all university IDs
        cursor.execute("SELECT id FROM university")
        university_ids = [row[0] for row in cursor.fetchall()]

        for i, university_id in enumerate(university_ids, 1):
            # Generate values for each field
            student_org_desc = generate_student_org_description()
            athletics_desc = generate_athletics_description()
            avg_rating = round(random.uniform(3.0, 5.0), 2)
            total_reviews = random.randint(50, 500)
            total_students = random.randint(5000, 50000)
            total_country_students = int(total_students * random.uniform(0.6, 0.9))
            acceptance_rate = round(random.uniform(0.1, 0.9), 2)

            # Update the university record
            cursor.execute("""
                UPDATE university 
                SET student_org_description = %s,
                    athletics_description = %s,
                    avg_rating = %s,
                    total_reviews = %s,
                    total_students = %s,
                    total_country_students = %s,
                    acceptance_rate = %s
                WHERE id = %s
            """, (
                student_org_desc,
                athletics_desc,
                avg_rating,
                total_reviews,
                total_students,
                total_country_students,
                acceptance_rate,
                university_id
            ))

            # Commit after each update
            conn.commit()
            print(f"[{i}/{total_universities}] Updated university ID: {university_id}")

        print("\nUpdate completed successfully!")

    except Exception as e:
        print(f"\nError: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    update_university_fields() 