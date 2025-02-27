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

- **Reviews & Ratings** (Optional)
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

- **POST /api/auth/register/**: Register a new user (Job Seeker or Employer).
- **POST /api/auth/login/**: Authenticate and generate JWT token for authenticated users.
- **POST /api/auth/logout/**: Logout and invalidate the JWT token.
- **POST /api/auth/password/reset/**: Send password reset link to the user's email.
- **POST /api/auth/password/change/**: Change password after receiving the reset token.

### 2. User Management

- **GET /api/users/**: List all users (Admin).
- **GET /api/users/{user_id}/**: Retrieve user profile details.
- **PATCH /api/users/{user_id}/**: Update user profile details.
- **PATCH /api/users/deactivate/**: Deactivate the user's account.
- **DELETE /api/users/{user_id}/**: Delete a user from the system (Admin).

### 3. Job Listings & Employers

- **POST /api/jobs/**: Employers create new job postings.
- **GET /api/jobs/**: View employer’s job listings (Employer).
- **PATCH /api/jobs/{job_id}/**: Update a job posting.
- **DELETE /api/jobs/{job_id}/close/**: Close or delete a job posting.
- **GET /api/jobs/**: Job Seekers can view job listings filtered by location, industry, or job type (Job seeker).
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

### **Users**
Manages user data, including Job Seekers and Employers. This model handles authentication, permissions, and roles, ensuring that users can only access the appropriate resources based on their roles (Job Seekers, Employers, Admins). It stores user details like email, password, name, and role. 

### **Admin Users**
Admin Users have elevated privileges within the platform, including managing user accounts, job postings, job applications, and generating reports. They have access to all system data and are responsible for overseeing the functionality of the platform.

### **Job Seekers**
The Job Seekers model stores information specific to users seeking employment. It includes personal details, skills, experience, and the job applications they’ve made. Job Seekers can apply for jobs, track their applications, and set preferences for job types and locations.

### **Job Seeker Interests**
This model allows Job Seekers to specify their areas of interest or preferred job roles. These interests help employers identify potential candidates that match the skills or industry types they are hiring for, and can be used to send tailored job recommendations to job seekers.

### **Fields of Interest**
Fields of Interest categorize the areas in which a Job Seeker or Employer is interested. These can include industries, job roles, or skill sets and help in matching job seekers with relevant job postings, ensuring that both parties find relevant opportunities more easily.

### **Employers**
The Employers model stores details of organizations posting jobs on the platform. Employers can create and manage job postings, view applications, and filter through job seekers based on skills, qualifications, and other criteria. This model also stores business-related information such as company name, location, and industry.

### **Jobs**
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
- **Deployment**: Docker, GitHub Actions (CI/CD), DigitalOcean

## Installation

To get started with the Job Board Backend:

### Prerequisites
- Python 3.x
- PostgreSQL
- Docker (for containerization)

### Step 1: Clone the repository
```bash
git clone https://github.com/yourusername/jobboard-backend.git
cd jobboard-backend

### Step 2: Install dependencies

### Step 3: Configure the database

### Step 4: Create a superuser (for admin access)

### Step 5: Run the development server

### Usage