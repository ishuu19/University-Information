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

def update_program_images():
    try:
        # Get list of image files from program_images folder
        image_folder = 'program_images'
        image_files = [f for f in os.listdir(image_folder) if f.endswith(('.jpg', '.jpeg', '.png'))]
        
        if not image_files:
            print("No images found in program_images folder!")
            return
        
        # Get all program IDs
        cursor.execute("SELECT id FROM program")
        program_ids = cursor.fetchall()
        
        # Update each program with a random image
        for program_id in program_ids:
            # Select a random image
            random_image = random.choice(image_files)
            # Create the relative path that will be used in the website
            image_path = f"/static/images/programs/{random_image}"
            
            # Update the database
            cursor.execute("""
                UPDATE program 
                SET image_url = %s 
                WHERE id = %s
            """, (image_path, program_id[0]))
            
            print(f"Updated program ID {program_id[0]} with image: {image_path}")
        
        # Commit the changes
        conn.commit()
        print("\nSuccessfully updated all program images!")
        
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    update_program_images() 