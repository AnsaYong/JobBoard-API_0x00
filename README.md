# Job Board Backend

## Overview

The **Job Board Backend** is a robust, scalable API designed to manage job postings, applications, user profiles, and notifications. Built with Django and Django REST Framework (DRF), the backend is optimized for handling high traffic and supports features such as role-based authentication, JWT token-based authorization, and real-time notifications. The backend also features a customizable admin dashboard for easy user and job management.

## Features

- **User Management**: 
  - User roles: Job Seekers, Employers, Admins.
  - Job Seekers and Employers with custom roles and permissions.
  - User registration, login, profile updates, password management, and user deactivation.
  - Admin functionality for user management, including role updates and deletions.

- **Job Listings & Employer Management**
  - Employers can create, update, and close job postings.
  - Employers can view and manage job applications.
  - Job Seekers can search for jobs using filters (location, industry, job type).
  - Search functionality with keyword matching for job titles, descriptions, and required skills.

- **Job Applications & Tracking**:
  - Job Seekers can apply for jobs, track application status, and withdraw applications.
  - Employers can view applications for each job posting and manage application status (e.g., "In Review", "Interview Scheduled").
  - Job Seekers can withdraw applications.

- **Notifications**
  - Notifications for job seekers and employers for application updates, new job postings, etc.
  - Ability to mark notifications as read or delete them.

- **Reviews & Ratings**
  - Submit and view job reviews for job postings.
  - Submit and view user reviews for employers/job seekers.

- **Reporting**
  - Admins can generate reports on job postings, user activity, and job applications.
  - Reports are available in formats like CSV or PDF.

- **Search & Filtering**
  - Advanced search functionality for job seekers to find jobs based on keywords, location, industry, and job type.
  - Filtering job listings for employers based on criteria like job type and location.

- **Admin Dashboard & Management**
  - Admins can manage users, including updating roles and deleting accounts.
  - Admin can view user details and job application data for reporting purposes.

## API Endpoints

### 1. Authentication & Users

- **POST /api/users/auth/register/**: Register a new user (Job Seeker or Employer).
- **POST /api/users/auth/login/**: Authenticate and generate JWT token for authenticated users.
- **POST /api/users/auth/logout/**: Logout and invalidate the JWT token.
- **POST /api/users/auth/password/request-reset/**: Send password reset link to the user's email.
- **POST /api/users/auth/password/reset/**: Reset the user's email password.
- **PUT /api/users/auth/password/change/**: Change password after receiving the reset token.
- **PATCH /api/users/auth/password/change/**: Change password after receiving the reset token.

### 2. User Management

- **GET /api/users/**: List users (Admin - all users; others - only themselves).
- **GET /api/users/{user_id}/**: Retrieve user profile details.
- **POST /api/users/**: Create a new user (System/Admin).
- **PUT /api/users/{user_id}/**: Update user profile details.
- **PATCH /api/users/{user_id}/**: Update user profile details.
- **DELETE /api/users/{user_id}/**: Delete a user from the system (Admin).
- **POST /api/users/{user_id}/deactivate/**: Deactivate the user's account.

### 3. Job Listings & Employers

- **GET /api/jobs/**: View job listings (filtered by location/industry/job type etc. or by Employer).
- **POST /api/jobs/**: Employers create new job postings.
- **GET /api/jobs/{job_id}**: View details of job posting.
- **PUT /api/jobs/{job_id}/**: Update a job posting.
- **PATCH /api/jobs/{job_id}/**: Update a job posting.
- **DELETE /api/jobs/{job_id}/close/**: Close or delete a job posting.
- **GET /api/jobs/search/**: Job Seekers can search for jobs by keyword.

### 4. Job Applications & Tracking

- **POST /api/jobs/{job_id}/applications/**: Job Seekers apply for a job.
- **GET /api/users/{user_id}/applications/**: List applications made by the authenticated Job Seeker.
- **DELETE /api/users/{user_id}/applications/{application_id}/withdraw/**: Withdraw an application by the Job Seeker.
- **GET /api/jobs/{job_id}/applications/**: Employers can view applications for a specific job.
- **PATCH /api/jobs/{job_id}/applications/{application_id}/status/**: Update the application status (e.g., "In Review", "Interview Scheduled").

### 5. Notifications

- **GET /api/users/{user_id}/notifications/**: Retrieve notifications for a user.
- **PATCH /api/users/{user_id}/notifications/{notification_id}/**: Mark notification as read.
- **DELETE /api/users/{user_id}/notifications/{notification_id}/**: Delete a notification.
- **POST /api/users/{user_id}/notifications/mark-all-read/**: Mark all notifications as read.

### 6. Admin Dashboard & Management

- **GET /api/users/**: List all users for the admin.
- **GET /api/users/{user_id}/**: View specific user details.
- **PATCH /api/users/{user_id}/role/**: Update a user’s role (e.g., Admin, Employer, Job Seeker).
- **DELETE /api/users/{user_id}/**: Delete a user.
- **POST /api/reports/**: Generate reports for job postings, user activity, and applications.

## Models

The backend uses the following key models:

### **User**
Manages user data, including Job Seekers and Employers. This model handles authentication, permissions, and roles, ensuring that users can only access the appropriate resources based on their roles (Job Seekers, Employers, Admins). It stores user details like email, password, name, and role.

### **JobBoardAdmin User**
Admin Users have elevated privileges within the platform, including managing user accounts, job postings, job applications, and generating reports. They have access to all system data and are responsible for overseeing the functionality of the platform.

### **Job Seeker**
The Job Seekers model stores information specific to users seeking employment. It includes personal details, skills, experience, and the job applications they’ve made. Job Seekers can apply for jobs, track their applications, and set preferences for job types and locations.

### **Job Seeker Interests**
This model allows Job Seekers to specify their areas of interest or preferred job roles. These interests help employers identify potential candidates that match the skills or industry types they are hiring for, and can be used to send tailored job recommendations to job seekers.

### **Fields of Interest**
Fields of Interest categorize the areas in which a Job Seeker or Employer is interested. These can include industries, job roles, or skill sets and help in matching job seekers with relevant job postings, ensuring that both parties find relevant opportunities more easily.

### **Employers**
The Employers model stores details of organizations posting jobs on the platform. Employers can create and manage job postings, view applications, and filter through job seekers based on skills, qualifications, and other criteria. This model also stores business-related information such as company name, location, and industry.

### **Job Posting**
This model contains job posting details, including job titles, descriptions, locations, required skills, compensation, and job type (full-time, part-time, etc.). Employers can create, update, and close jobs, while job seekers can browse available listings.

### **Job Applications**
The Job Applications model represents applications submitted by Job Seekers for specific job postings. It includes the status of the application (e.g., "In Review", "Interview Scheduled"), the date of submission, and any relevant documents submitted by the Job Seeker (e.g., resumes or cover letters). Employers can review these applications and update their statuses accordingly.

### **Notifications**
The Notifications model stores messages or alerts for users based on specific actions or events. These could be related to job application status updates, new job postings, or reminders about upcoming application deadlines. Notifications can be read, deleted, or marked as read by the users.

### **Job Reviews**
This model allows Job Seekers to review employers or specific job postings they have applied to or worked with. Reviews typically include ratings and feedback on the job, the employer, and the overall experience. Employers can also leave feedback about the Job Seekers.

### **Reports**
The Reports model allows Admin users to generate reports on various system metrics such as job postings, user activity, job application statuses, and performance. Reports are typically in CSV or PDF format and provide insights into platform usage and trends.

### **Search Index**
The Search Index model is used to enhance search functionality across the platform. It indexes job postings, user profiles, and other data to improve the performance and relevance of search queries. This index helps Job Seekers find jobs more efficiently and allows Employers to filter applicants based on relevant criteria.


## Technology Stack

- **Backend Framework**: Django, Django REST Framework
- **Database**: PostgreSQL
- **Authentication**: JWT-based authentication (JSON Web Tokens)
- **Caching**: Redis (for real-time notifications)
- **Messaging/Notifications**: Celery & Redis for background tasks (notifications)
- **Search**: Full-text search with PostgreSQL
- ***Unit and Integration testing**: Pytest
- **Deployment**: Heroku

## Installation

To get started with the Job Board Backend:

### Prerequisites
Ensure you have the following installed:
- Python 3.x – Required to run the Django application.
- PostgreSQL – The database used for storing job board data.
- Redis – Required for background task processing (e.g., Celery).
- Docker (Optional) – For containerized deployment.

### Step 1: Clone the Repository
Clone the project and navigate to the directory:
```bash
git clone https://github.com/yourusername/jobboard-backend.git
cd jobboard-backend
```

### Step 2: Install Dependencies
Create a virtual environment and install required packages:
```
python -m venv .venv
source .venv/bin/activate # On Windows use: .venv\Scripts\activate
pip install -r requirements.txt
```

### Step 3: Configure the database & Redis
1. Create a PostgreSQL database:
```
CREATE DATABASE jobboard_db;
```

2. Ensure Redis is running:
- if installed locally, start Redis:
```
redis-server
```

- If using Docker, start a Redis container:
```
docker run -d --name redis -p 6379:6379 redis
```

3. Update the .env file with your database and Redis configurations:
```
DB_NAME=jobboard_db  
DB_USER=your_username  
DB_PASSWORD=your_password  
DB_HOST=localhost  
DB_PORT=5432  

REDIS_URL=redis://localhost:6379/0
```

### Step 4: Apply Migrations & Create Superuser
Run database migrations:
```
python manage.py migrate
```

Create a superuser for admin access
```
python manage.py createsuperuser
```

### Step 5: Start Required Services
1. Run Redis (if not already running):
```
redis-server
```

2. Start Celery (for background tasks):
```
celery -A jobboard worker --loglevel=info
```

3. Run the Djago Development Server
```
python manage.py runserver
```
The server will be available at: http://127.0.0.1:8000/

### Optional: Run with Docker
If you prefer using Docker, build and run the containers:
```
docker-compose up --build
```

### Usage
- Access the Admin Panel: http://127.0.0.1:8000/admin/
- API endpoints available under /api/
- API documentation available under /api/docs

## Contributing
I welcome contributions! If you'd like to contribute:

1. Fork the repository.
2. Create a new branch (git checkout -b feature-branch).
3. Commit your changes (git commit -m "Add new feature").
4. Push to the branch (git push origin feature-branch).
5. Open a pull request.

## Troubleshooting & Support
If you run into any issues:

- Check the logs (docker logs <container_id> or python manage.py runserver).
- Make sure PostgreSQL and Redis are running.
- Refer to the Django & Celery documentation.
- Open an issue on GitHub if needed.

## License
This project is licensed under the MIT License. See LICENSE for details.

## Contact & Feedback
For questions or feedback, feel free to reach out:
📧 Email: ansahmbomyong@gmail.com
🐙 GitHub Issues: Open an Issue