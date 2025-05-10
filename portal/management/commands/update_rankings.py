from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Updates university rankings with unique values'

    def handle(self, *args, **options):
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
                    self.stdout.write(
                        self.style.SUCCESS(f"Updated {university[1]} with ranking {index}")
                    )
                
                self.stdout.write(
                    self.style.SUCCESS("Successfully updated all university rankings!")
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Error updating rankings: {str(e)}")
            ) 