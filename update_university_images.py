import mysql.connector
import os
import random

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

def update_university_images():
    try:
        # Get list of image files from uni_images folder
        image_folder = 'uni_images'
        image_files = [f for f in os.listdir(image_folder) if f.endswith(('.jpg', '.jpeg', '.png'))]
        
        if not image_files:
            print("No images found in uni_images folder!")
            return
        
        # Get all university IDs
        cursor.execute("SELECT id FROM university")
        university_ids = cursor.fetchall()
        
        # Update each university with a random image
        for uni_id in university_ids:
            # Select a random image
            random_image = random.choice(image_files)
            # Create the relative path that will be used in the website
            image_path = f"/static/images/universities/{random_image}"
            
            # Update the database
            cursor.execute("""
                UPDATE university 
                SET image_url = %s 
                WHERE id = %s
            """, (image_path, uni_id[0]))
            
            print(f"Updated university ID {uni_id[0]} with image: {image_path}")
        
        # Commit the changes
        conn.commit()
        print("\nSuccessfully updated all university images!")
        
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    update_university_images() 