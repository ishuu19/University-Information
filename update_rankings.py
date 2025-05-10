from django.db import connection

def update_university_rankings():
    try:
        with connection.cursor() as cursor:
            # First, get all universities ordered by their current ranking
            cursor.execute("""
                SELECT id, name, world_university_ranking 
                FROM university 
                WHERE world_university_ranking IS NOT NULL 
                ORDER BY world_university_ranking
            """)
            universities = cursor.fetchall()
            
            # Update each university with a new unique ranking
            for index, university in enumerate(universities, start=1):
                cursor.execute("""
                    UPDATE university 
                    SET world_university_ranking = %s 
                    WHERE id = %s
                """, [index, university[0]])
                print(f"Updated {university[1]} with ranking {index}")
            
            print("Successfully updated all university rankings!")
            
    except Exception as e:
        print(f"Error updating rankings: {str(e)}")

if __name__ == "__main__":
    update_university_rankings() 