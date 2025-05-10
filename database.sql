-- Create the Database
CREATE DATABASE universityadmissiondb;
USE universityadmissiondb;

-- University Type Table
CREATE TABLE university_type (
    id INT AUTO_INCREMENT PRIMARY KEY,
    type_name ENUM('Private', 'Public', 'Other')
);

-- University Table
CREATE TABLE university (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    two_line_info TEXT,
    country VARCHAR(100),
    world_university_ranking INT,
    type_id INT,
    founded_year INT,
    image_url TEXT,
    location VARCHAR(255),
    application_deadline DATE,
    FOREIGN KEY (type_id) REFERENCES university_type(id)
);

-- University Contact Table
CREATE TABLE university_contact (
    id INT AUTO_INCREMENT PRIMARY KEY,
    university_id INT,
    contact_email VARCHAR(255) ,
    contact_phone VARCHAR(50) ,
    uni_website VARCHAR(255) ,
    FOREIGN KEY (university_id) REFERENCES university(id) ON DELETE CASCADE
);

-- University Description Table
CREATE TABLE university_description (
    id INT AUTO_INCREMENT PRIMARY KEY,
    university_id INT,
    short_description TEXT,
    housing_description VARCHAR(255),
    dining_description VARCHAR(255),
    student_org_description VARCHAR(255),
    athletics_description VARCHAR(255),
    FOREIGN KEY (university_id) REFERENCES university(id) ON DELETE CASCADE
);

-- University Stats Table
CREATE TABLE university_stats (
    id INT AUTO_INCREMENT PRIMARY KEY,
    university_id INT,
    avg_rating DECIMAL(2,1),
    total_reviews INT,
    total_students INT,
    total_country_students INT,
    acceptance_rate DECIMAL(5,2),
    student_faculty_ratio DECIMAL(5,2),
    avg_tuition DECIMAL(10,2),
    estimated_cost_of_living DECIMAL(10,2),
    FOREIGN KEY (university_id) REFERENCES university(id) ON DELETE CASCADE
);

-- University Admission Requirements Table
CREATE TABLE uni_admission_requirements (
    id INT AUTO_INCREMENT PRIMARY KEY,
    university_id INT,
    req TEXT,
    language_req TEXT,
    extra_docs TEXT,
    standardized_test_scores TEXT,
    FOREIGN KEY (university_id) REFERENCES university(id) ON DELETE CASCADE
);

-- Degrees Information Table
CREATE TABLE degree (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100)
);

-- Field Information Table
CREATE TABLE field (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100)
);

-- Programs Table
CREATE TABLE program (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255),
    university_id INT,
    degree_id INT,
    field_id INT,
    program_overview TEXT,
    image_url TEXT,
    FOREIGN KEY (university_id) REFERENCES university(id) ON DELETE CASCADE,
    FOREIGN KEY (degree_id) REFERENCES degree(id),
    FOREIGN KEY (field_id) REFERENCES field(id)
);

-- Program Contact Table
CREATE TABLE program_contact (
    id INT AUTO_INCREMENT PRIMARY KEY,
    program_id INT,
    program_email VARCHAR(255),
    program_phone VARCHAR(50),
    program_website VARCHAR(255),
    FOREIGN KEY (program_id) REFERENCES program(id) ON DELETE CASCADE
);

-- Program Schedule Table
CREATE TABLE program_schedule (
    id INT AUTO_INCREMENT PRIMARY KEY,
    program_id INT,
    duration VARCHAR(50),
    credits INT,
    start_semester ENUM('Fall', 'Summer', 'Winter'),
    application_fee DECIMAL(10,2),
    application_deadline DATE,
    application_opens_date DATE,
    early_decision DATE,
    regular_decision DATE,
    start_date DATE,
    result_publish DATE,
    FOREIGN KEY (program_id) REFERENCES program(id) ON DELETE CASCADE
);

-- Program Requirements Table
CREATE TABLE program_requirements (
    id INT AUTO_INCREMENT PRIMARY KEY,
    program_id INT,
    tuition DECIMAL(10,2),
    taught_language VARCHAR(50),
    test_score_SAT INT,
    test_score_TOEFL INT,
    test_score_IELTS DECIMAL(3,1),
    additional_req TEXT,
    FOREIGN KEY (program_id) REFERENCES program(id) ON DELETE CASCADE
);

-- Financial Aid and Scholarships Table
CREATE TABLE financial_aid_and_scholarships (
    id INT AUTO_INCREMENT PRIMARY KEY,
    program_id INT,
    aid_name VARCHAR(255),
    amount DECIMAL(10,2),
    type_and_for_whom TEXT,
    eligibility TEXT,
    renewal_criteria TEXT,
    FOREIGN KEY (program_id) REFERENCES program(id) ON DELETE CASCADE
);

-- Professional Scopes Table
CREATE TABLE professional_scopes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    program_id INT,
    profession VARCHAR(100),
    more_depth_in_profession TEXT,
    FOREIGN KEY (program_id) REFERENCES program(id) ON DELETE CASCADE
);

-- Program Reviews Table
CREATE TABLE program_reviews (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255),
    rating DECIMAL(3,2),
    program_id INT,
    university_id INT,
    graduation_year YEAR,
    review TEXT,
    posted_date DATE,
    FOREIGN KEY (program_id) REFERENCES program(id) ON DELETE CASCADE,
    FOREIGN KEY (university_id) REFERENCES university(id) ON DELETE CASCADE
);

-- Users Table
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    email VARCHAR(255),
    phone VARCHAR(50),
    address VARCHAR(255),
    bio TEXT,
    image_url TEXT
);

-- Applications Table
CREATE TABLE applications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    university_id INT,
    program_id INT,
    start_term VARCHAR(50),
    personal_statement TEXT,
    status ENUM('Pending', 'Submitted', 'Reviewed', 'Accepted', 'Rejected'),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (university_id) REFERENCES university(id) ON DELETE CASCADE,
    FOREIGN KEY (program_id) REFERENCES program(id) ON DELETE CASCADE
);

-- Saved Universities Table
CREATE TABLE saved_universities (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    university_id INT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (university_id) REFERENCES university(id) ON DELETE CASCADE
);

-- Saved Programs Table
CREATE TABLE saved_program (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    program_id INT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (program_id) REFERENCES program(id) ON DELETE CASCADE
);

-- User Documents Table
CREATE TABLE user_documents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    diploma TEXT,
    academic_transcripts TEXT,
    resume TEXT,
    passport TEXT,
    standardized_test_results TEXT,
    language_test_results TEXT,
    letter_of_recommendation TEXT,
    ECA TEXT,
    other_documents TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Blog Table
CREATE TABLE blog (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255),
    posted_date DATE,
    author_id INT,
    category VARCHAR(100),
    location VARCHAR(255),
    content TEXT,
    tags VARCHAR(500),
    image_url TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (author_id) REFERENCES users(id) ON DELETE SET NULL
);

-- Blog Comments Table
CREATE TABLE blog_comments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    blog_id INT,
    user_id INT,
    email VARCHAR(255),
    comment TEXT,
    posted_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (blog_id) REFERENCES blog(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Program Key Modules Table
CREATE TABLE program_key_module (
    id INT AUTO_INCREMENT PRIMARY KEY,
    program_id INT,
    module_name VARCHAR(255),
    description TEXT,
    FOREIGN KEY (program_id) REFERENCES program(id) ON DELETE CASCADE
);

-- Scholarship General Requirements Table
CREATE TABLE scholarship_general_req (
    id INT AUTO_INCREMENT PRIMARY KEY,
    program_id INT,
    requirement_type VARCHAR(100),
    requirement_details TEXT,
    FOREIGN KEY (program_id) REFERENCES program(id) ON DELETE CASCADE
);

-- Create Indexes for better performance
CREATE INDEX idx_programs_university_id ON program(university_id);
CREATE INDEX idx_programs_degree_id ON program(degree_id);
CREATE INDEX idx_program_requirements_program_id ON program_requirements(program_id);
CREATE INDEX idx_applications_user_id ON applications(user_id);
CREATE INDEX idx_applications_university_id ON applications(university_id);
CREATE INDEX idx_applications_program_id ON applications(program_id);