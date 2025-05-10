import mysql.connector
import random
from datetime import datetime, timedelta
from faker import Faker
import numpy as np

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

# Real university name components
university_prefixes = [
    'State', 'National', 'International', 'Global', 'United', 'American', 'European',
    'Pacific', 'Atlantic', 'Central', 'Northern', 'Southern', 'Eastern', 'Western',
    'Metropolitan', 'Technical', 'Polytechnic', 'Liberal Arts', 'Science and Technology',
    'Medical', 'Engineering', 'Business', 'Arts and Sciences'
]

university_suffixes = [
    'University', 'College', 'Institute', 'Academy', 'School', 'University of Technology',
    'University of Science', 'University of Arts', 'University of Business',
    'University of Engineering', 'University of Medicine'
]

# University types
university_types = [
    {'type_name': 'Public'},
    {'type_name': 'Private'},
    {'type_name': 'Other'}
]

# Degrees
degrees = [
    {'name': 'Bachelor'},
    {'name': 'Master'},
    {'name': 'PhD'},
    {'name': 'Associate'},
    {'name': 'Diploma'}
]

# Fields of study
fields = [
    {'name': 'Computer Science'},
    {'name': 'Engineering'},
    {'name': 'Business'},
    {'name': 'Medicine'},
    {'name': 'Arts'}
]

# Real program templates
program_templates = [
    # Computer Science Programs
    {
        'degree': 'Bachelor',
        'field': 'Computer Science',
        'name': 'Computer Science',
        'modules': ['Data Structures', 'Algorithms', 'Database Systems', 'Operating Systems', 
                   'Computer Networks', 'Software Engineering', 'Artificial Intelligence', 
                   'Machine Learning', 'Web Development', 'Mobile App Development']
    },
    {
        'degree': 'Master',
        'field': 'Computer Science',
        'name': 'Advanced Computer Science',
        'modules': ['Advanced Algorithms', 'Distributed Systems', 'Cloud Computing', 
                   'Big Data Analytics', 'Cybersecurity', 'Deep Learning', 
                   'Natural Language Processing', 'Computer Vision', 'Software Architecture', 
                   'Research Methods']
    },
    # Engineering Programs
    {
        'degree': 'Bachelor',
        'field': 'Engineering',
        'name': 'Mechanical Engineering',
        'modules': ['Thermodynamics', 'Fluid Mechanics', 'Materials Science', 
                   'Machine Design', 'Control Systems', 'Manufacturing Processes', 
                   'Heat Transfer', 'Robotics', 'CAD/CAM', 'Engineering Mathematics']
    },
    {
        'degree': 'Bachelor',
        'field': 'Engineering',
        'name': 'Electrical Engineering',
        'modules': ['Circuit Theory', 'Electronics', 'Power Systems', 'Control Systems', 
                   'Digital Systems', 'Electromagnetic Theory', 'Signal Processing', 
                   'Microprocessors', 'Power Electronics', 'Communication Systems']
    },
    # Business Programs
    {
        'degree': 'Bachelor',
        'field': 'Business',
        'name': 'Business Administration',
        'modules': ['Accounting', 'Marketing', 'Finance', 'Management', 'Economics', 
                   'Business Law', 'Operations Management', 'Business Strategy', 
                   'International Business', 'Business Ethics']
    },
    {
        'degree': 'Master',
        'field': 'Business',
        'name': 'MBA',
        'modules': ['Advanced Finance', 'Strategic Management', 'Leadership', 
                   'Business Analytics', 'Global Business', 'Entrepreneurship', 
                   'Marketing Strategy', 'Operations Strategy', 'Business Ethics', 
                   'Corporate Governance']
    },
    # Medical Programs
    {
        'degree': 'Bachelor',
        'field': 'Medicine',
        'name': 'Pre-Medical Studies',
        'modules': ['Biology', 'Chemistry', 'Physics', 'Anatomy', 'Physiology', 
                   'Biochemistry', 'Genetics', 'Microbiology', 'Psychology', 
                   'Medical Ethics']
    },
    {
        'degree': 'Master',
        'field': 'Medicine',
        'name': 'Public Health',
        'modules': ['Epidemiology', 'Biostatistics', 'Health Policy', 'Environmental Health', 
                   'Health Management', 'Global Health', 'Health Promotion', 
                   'Disease Prevention', 'Health Economics', 'Research Methods']
    },
    # Arts Programs
    {
        'degree': 'Bachelor',
        'field': 'Arts',
        'name': 'Fine Arts',
        'modules': ['Drawing', 'Painting', 'Sculpture', 'Art History', 'Color Theory', 
                   'Digital Art', 'Printmaking', 'Photography', 'Art Criticism', 
                   'Contemporary Art']
    },
    {
        'degree': 'Master',
        'field': 'Arts',
        'name': 'Digital Media Arts',
        'modules': ['Digital Design', 'Animation', 'Interactive Media', 'Visual Effects', 
                   'Game Design', 'Web Design', 'Motion Graphics', '3D Modeling', 
                   'Digital Storytelling', 'Media Theory']
    }
]

# Professional scopes for each field
professional_scopes = {
    'Computer Science': [
        {'profession': 'Software Developer', 'details': ['Frontend Developer', 'Backend Developer', 'Full Stack Developer', 'Mobile Developer', 'DevOps Engineer']},
        {'profession': 'Data Scientist', 'details': ['Machine Learning Engineer', 'Data Analyst', 'Business Intelligence Analyst', 'AI Researcher', 'Data Engineer']},
        {'profession': 'Systems Administrator', 'details': ['Network Administrator', 'Cloud Architect', 'Security Specialist', 'Database Administrator', 'IT Manager']}
    ],
    'Engineering': [
        {'profession': 'Mechanical Engineer', 'details': ['Design Engineer', 'Manufacturing Engineer', 'Research Engineer', 'Project Engineer', 'Quality Engineer']},
        {'profession': 'Electrical Engineer', 'details': ['Power Systems Engineer', 'Control Systems Engineer', 'Electronics Engineer', 'Communications Engineer', 'Research Engineer']}
    ],
    'Business': [
        {'profession': 'Business Analyst', 'details': ['Financial Analyst', 'Market Research Analyst', 'Operations Analyst', 'Strategy Consultant', 'Business Intelligence Analyst']},
        {'profession': 'Project Manager', 'details': ['Program Manager', 'Portfolio Manager', 'Agile Coach', 'Technical Project Manager', 'Business Project Manager']}
    ],
    'Medicine': [
        {'profession': 'Medical Researcher', 'details': ['Clinical Researcher', 'Laboratory Researcher', 'Epidemiologist', 'Biostatistician', 'Medical Writer']},
        {'profession': 'Healthcare Administrator', 'details': ['Hospital Administrator', 'Clinic Manager', 'Health Policy Analyst', 'Healthcare Consultant', 'Medical Practice Manager']}
    ],
    'Arts': [
        {'profession': 'Digital Artist', 'details': ['Graphic Designer', 'UI/UX Designer', 'Motion Graphics Artist', '3D Artist', 'Digital Illustrator']},
        {'profession': 'Art Director', 'details': ['Creative Director', 'Visual Designer', 'Brand Manager', 'Exhibition Curator', 'Art Consultant']}
    ]
}

# Initialize lookup tables
def initialize_lookup_tables():
    # Insert university types
    for type_data in university_types:
        cursor.execute("""
            INSERT INTO university_type (type_name)
            VALUES (%s)
        """, (type_data['type_name'],))
    
    # Insert degrees
    for degree_data in degrees:
        cursor.execute("""
            INSERT INTO degree (name)
            VALUES (%s)
        """, (degree_data['name'],))
    
    # Insert fields
    for field_data in fields:
        cursor.execute("""
            INSERT INTO field (name)
            VALUES (%s)
        """, (field_data['name'],))
    
    conn.commit()

# Generate realistic university name
def generate_university_name():
    prefix = random.choice(university_prefixes)
    suffix = random.choice(university_suffixes)
    location = fake.city()
    return f"{prefix} {location} {suffix}"

# Generate university data
def generate_university_data(num_universities=10000):
    universities = []
    used_names = set()  # To ensure unique university names
    used_rankings = set()  # To ensure unique rankings
    
    for _ in range(num_universities):
        while True:
            name = generate_university_name()
            if name not in used_names:
                used_names.add(name)
                break
        
        while True:
            ranking = random.randint(1, 1000)
            if ranking not in used_rankings:
                used_rankings.add(ranking)
                break
        
        location = fake.city()
        country = fake.country()
        uni_data = {
            'name': name,
            'two_line_info': f"A leading institution in {location}, {country}. " + fake.text(max_nb_chars=100),
            'country': country,
            'world_university_ranking': ranking,
            'type_id': random.randint(1, len(university_types)),
            'founded_year': random.randint(1800, 2020),
            'image_url': f"https://example.com/universities/{fake.uuid4()}.jpg",
            'location': f"{location}, {country}",
            'application_deadline': (datetime.now() + timedelta(days=random.randint(30, 365))).strftime('%Y-%m-%d'),
            'short_description': fake.text(max_nb_chars=200),
            'housing_description': f"Modern on-campus housing with {random.choice(['single', 'double', 'suite'])} room options",
            'dining_description': f"Multiple dining halls serving {random.choice(['international', 'local', 'continental'])} cuisine",
            'student_faculty_ratio': round(random.uniform(10, 30), 2),
            'avg_tuition': round(random.uniform(5000, 50000), 2),
            'estimated_cost_of_living': round(random.uniform(10000, 30000), 2)
        }
        universities.append(uni_data)
    return universities

# Generate university contact data
def generate_university_contact(university_id):
    return {
        'university_id': university_id,
        'contact_email': fake.email(),
        'contact_phone': fake.phone_number(),
        'uni_website': fake.url()
    }

# Generate university admission requirements
def generate_admission_requirements(university_id):
    return {
        'university_id': university_id,
        'req': f"Minimum GPA: {round(random.uniform(2.0, 4.0), 2)}\n" +
               f"SAT Score: {random.randint(1000, 1600)}\n" +
               f"ACT Score: {random.randint(20, 36)}",
        'language_req': f"TOEFL: {random.randint(60, 120)}\n" +
               f"IELTS: {round(random.uniform(5.0, 9.0), 1)}",
        'extra_docs': "1. Official transcripts\n2. Letters of recommendation\n3. Statement of purpose",
        'standardized_test_scores': f"SAT Subject Tests (optional)\nGRE: {random.randint(260, 340)}"
    }

# Generate program data
def generate_program_data(university_id):
    programs = []
    # We want 15-20 programs per university
    num_programs = random.randint(15, 20)
    
    # Create variations of each program template
    for template in program_templates:
        # Generate 1-3 variations of this program
        variations = random.randint(1, 3)
        for _ in range(variations):
            if len(programs) >= num_programs:
                break
                
            # Get degree_id based on template's degree
            cursor.execute("SELECT id FROM degree WHERE name = %s", (template['degree'],))
            degree_result = cursor.fetchone()
            if not degree_result:
                continue
            degree_id = degree_result[0]
            
            # Get field_id based on template's field
            cursor.execute("SELECT id FROM field WHERE name = %s", (template['field'],))
            field_result = cursor.fetchone()
            if not field_result:
                continue
            field_id = field_result[0]
            
            program_data = {
                'name': f"{template['name']} - {fake.word().title()} Specialization" if variations > 1 else template['name'],
                'university_id': university_id,
                'degree_id': degree_id,
                'field_id': field_id,
                'program_overview': f"This {template['degree']} program in {template['name']} provides comprehensive education in {template['field']}. " + fake.text(max_nb_chars=200),
                'image_url': f"https://example.com/programs/{fake.uuid4()}.jpg",
                'program_email': fake.email(),
                'program_phone': fake.phone_number(),
                'program_website': fake.url(),
                'duration': f"{random.randint(2, 6)} years",
                'credits': random.randint(120, 180),
                'start_semester': random.choice(['Fall', 'Spring', 'Winter']),
                'application_fee': round(random.uniform(50, 200), 2),
                'application_deadline': (datetime.now() + timedelta(days=random.randint(30, 365))).strftime('%Y-%m-%d'),
                'application_opens_date': (datetime.now() + timedelta(days=random.randint(-30, 30))).strftime('%Y-%m-%d'),
                'early_decision': (datetime.now() + timedelta(days=random.randint(60, 180))).strftime('%Y-%m-%d'),
                'regular_decision': (datetime.now() + timedelta(days=random.randint(180, 365))).strftime('%Y-%m-%d'),
                'start_date': (datetime.now() + timedelta(days=random.randint(365, 730))).strftime('%Y-%m-%d'),
                'result_publish': (datetime.now() + timedelta(days=random.randint(30, 90))).strftime('%Y-%m-%d'),
                'tuition': round(random.uniform(5000, 50000), 2),
                'taught_language': random.choice(['English', 'Spanish', 'French', 'German', 'Chinese']),
                'test_score_SAT': random.randint(1000, 1600),
                'test_score_TOEFL': random.randint(60, 120),
                'test_score_IELTS': round(random.uniform(5.0, 9.0), 1),
                'additional_req': fake.text(max_nb_chars=200)
            }
            programs.append(program_data)
    
    return programs

# Generate financial aid data
def generate_financial_aid_data(program_id, field):
    aid_types = {
        'Computer Science': ['Technology Scholarship', 'Innovation Grant', 'STEM Scholarship'],
        'Engineering': ['Engineering Excellence Award', 'Technical Innovation Grant', 'STEM Scholarship'],
        'Business': ['Business Leadership Scholarship', 'Entrepreneurship Grant', 'Management Excellence Award'],
        'Medicine': ['Medical Research Grant', 'Healthcare Leadership Scholarship', 'Public Health Award'],
        'Arts': ['Creative Arts Scholarship', 'Digital Media Grant', 'Fine Arts Award']
    }
    
    aids = []
    num_aids = random.randint(5, 10)
    for _ in range(num_aids):
        aid_type = random.choice(aid_types.get(field, ['Academic Excellence Scholarship', 'Merit Scholarship', 'Need-based Grant']))
        aid_data = {
            'program_id': program_id,
            'aid_name': f"{aid_type} - {fake.word().title()}",
            'amount': round(random.uniform(1000, 50000), 2),
            'type_and_for_whom': f"{aid_type} for {field} students",
            'eligibility': f"Open to {field} students with minimum GPA of {random.uniform(2.5, 3.5):.1f}",
            'renewal_criteria': f"Maintain GPA of {random.uniform(2.5, 3.5):.1f} and complete {random.randint(12, 18)} credits per semester"
        }
        aids.append(aid_data)
    return aids

# Generate professional scopes
def generate_professional_scopes(program_id, field):
    scopes = []
    field_scopes = professional_scopes.get(field, [])
    if field_scopes:
        for scope in field_scopes:
            scope_data = {
                'program_id': program_id,
                'profession': scope['profession'],
                'more_depth_in_profession': scope['details']
            }
            scopes.append(scope_data)
    return scopes

# Generate program modules
def generate_program_modules(program_id, field):
    modules = []
    field_modules = next((p['modules'] for p in program_templates if p['field'] == field), None)
    if field_modules:
        for module in field_modules:
            module_data = {
                'program_id': program_id,
                'module_name': module
            }
            modules.append(module_data)
    return modules

# Generate program reviews
def generate_program_reviews(program_id, university_id):
    reviews = []
    num_reviews = random.randint(5, 15)
    for _ in range(num_reviews):
        review_data = {
            'program_id': program_id,
            'university_id': university_id,
            'name': fake.name(),
            'rating': round(random.uniform(1, 5), 2),
            'graduation_year': random.randint(2015, 2023),
            'review': fake.text(max_nb_chars=500),
            'posted_date': (datetime.now() - timedelta(days=random.randint(1, 365))).strftime('%Y-%m-%d')
        }
        reviews.append(review_data)
    return reviews

# Insert data into database
def insert_data():
    try:
        print("Initializing lookup tables...")
        # Initialize lookup tables
        initialize_lookup_tables()
        print("Lookup tables initialized successfully!")
        
        # Generate and insert universities one by one
        total_universities = 10000
        total_programs = 0

        for i in range(total_universities):
            # Generate single university
            uni = generate_university_data(1)[0]
            
            # Insert university
            cursor.execute("""
                INSERT INTO university (name, two_line_info, country, world_university_ranking,
                type_id, founded_year, image_url, location, application_deadline,
                short_description, housing_description, dining_description,
                student_faculty_ratio, avg_tuition, estimated_cost_of_living)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                uni['name'], uni['two_line_info'], uni['country'],
                uni['world_university_ranking'], uni['type_id'], uni['founded_year'],
                uni['image_url'], uni['location'], uni['application_deadline'],
                uni['short_description'], uni['housing_description'], uni['dining_description'],
                uni['student_faculty_ratio'], uni['avg_tuition'], uni['estimated_cost_of_living']
            ))
            university_id = cursor.lastrowid
            print(f"\n[{i+1}/{total_universities}] Inserted university: {uni['name']} (ID: {university_id})")

            # Insert university contact
            contact = generate_university_contact(university_id)
            cursor.execute("""
                INSERT INTO university_contact (university_id, contact_email, contact_phone, uni_website)
                VALUES (%s, %s, %s, %s)
            """, (
                contact['university_id'], contact['contact_email'],
                contact['contact_phone'], contact['uni_website']
            ))
            print(f"  ✓ Added contact information")

            # Insert university admission requirements
            requirements = generate_admission_requirements(university_id)
            cursor.execute("""
                INSERT INTO uni_admission_requirements (university_id, req, language_req,
                extra_docs, standardized_test_scores)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                requirements['university_id'], requirements['req'],
                requirements['language_req'], requirements['extra_docs'],
                requirements['standardized_test_scores']
            ))
            print(f"  ✓ Added admission requirements")

            # Generate and insert programs for this university
            programs = generate_program_data(university_id)
            print(f"  ✓ Adding {len(programs)} programs:")
            
            for program in programs:
                cursor.execute("""
                    INSERT INTO program (name, university_id, degree_id, field_id, program_overview,
                    image_url, program_email, program_phone, program_website, duration, credits,
                    start_semester, application_fee, application_deadline, application_opens_date,
                    early_decision, regular_decision, start_date, result_publish, tuition,
                    taught_language, test_score_SAT, test_score_TOEFL, test_score_IELTS, additional_req)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    program['name'], program['university_id'], program['degree_id'],
                    program['field_id'], program['program_overview'], program['image_url'],
                    program['program_email'], program['program_phone'], program['program_website'],
                    program['duration'], program['credits'], program['start_semester'],
                    program['application_fee'], program['application_deadline'],
                    program['application_opens_date'], program['early_decision'],
                    program['regular_decision'], program['start_date'], program['result_publish'],
                    program['tuition'], program['taught_language'], program['test_score_SAT'],
                    program['test_score_TOEFL'], program['test_score_IELTS'],
                    program['additional_req']
                ))
                program_id = cursor.lastrowid
                total_programs += 1
                print(f"    ✓ Added program: {program['name']} (ID: {program_id})")

                # Get field name for this program
                cursor.execute("SELECT name FROM field WHERE id = %s", (program['field_id'],))
                field_name = cursor.fetchone()[0]

                # Insert financial aids
                aids = generate_financial_aid_data(program_id, field_name)
                for aid in aids:
                    cursor.execute("""
                        INSERT INTO financial_aid_and_scholarships 
                        (program_id, aid_name, amount, type_and_for_whom, eligibility, renewal_criteria)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (
                        aid['program_id'], aid['aid_name'], aid['amount'],
                        aid['type_and_for_whom'], aid['eligibility'], aid['renewal_criteria']
                    ))
                print(f"      ✓ Added {len(aids)} financial aids")

                # Insert professional scopes
                scopes = generate_professional_scopes(program_id, field_name)
                for scope in scopes:
                    cursor.execute("""
                        INSERT INTO professional_scopes (program_id, profession, more_depth_in_profession)
                        VALUES (%s, %s, %s)
                    """, (
                        scope['program_id'], scope['profession'],
                        ','.join(scope['more_depth_in_profession'])
                    ))
                print(f"      ✓ Added {len(scopes)} professional scopes")

                # Insert program modules
                modules = generate_program_modules(program_id, field_name)
                for module in modules:
                    cursor.execute("""
                        INSERT INTO program_key_module (program_id, module_name)
                        VALUES (%s, %s)
                    """, (module['program_id'], module['module_name']))
                print(f"      ✓ Added {len(modules)} program modules")

                # Insert program reviews
                reviews = generate_program_reviews(program_id, university_id)
                for review in reviews:
                    cursor.execute("""
                        INSERT INTO program_reviews (program_id, university_id, name, rating,
                        graduation_year, review, posted_date)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (
                        review['program_id'], review['university_id'],
                        review['name'], review['rating'],
                        review['graduation_year'], review['review'],
                        review['posted_date']
                    ))
                print(f"      ✓ Added {len(reviews)} program reviews")

            # Commit after each university to avoid transaction size issues
            conn.commit()
            print(f"\n✓ Successfully completed inserting all data for university: {uni['name']}")
            print("-" * 80)

        print("\nFinal Statistics:")
        print(f"Total universities inserted: {total_universities}")
        print(f"Total programs inserted: {total_programs}")

    except Exception as e:
        print(f"\nError: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    try:
        insert_data()
    except KeyboardInterrupt:
        print("\nScript interrupted by user. Cleaning up...")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        print("Cleanup complete.") 