# HopeBridge

## Project Overview

**HopeBridge** is a Django-based web portal for NGOs to manage donations, volunteers, events, relief programs, food drives, and book donations. Donors can track their sponsored students/families. The platform includes an admin dashboard and a live analytics dashboard to keep track of donation stats, event budgets, and volunteer hours. 

This project is built as a practical, student-friendly NGO management system, showcasing core web development concepts using Django.

## Tech Stack

- **Backend:** Python, Django 5.2
- **Frontend:** HTML, Django Templates, Bootstrap 5
- **Database:** SQLite

## Features

The project is organized into 5 core apps, each with its own features:

### Donors
- Full CRUD (Create, Read, Update, Delete) management.
- Keep track of donor details and their donation history.

### Volunteers
- Full CRUD management.
- Log volunteer information and the total hours they have contributed.

### Donations
- Full CRUD management.
- Support for various donation types (money, food, clothes, books).
- **Invoices:** Professional donation invoice/receipt generation with formatted invoice numbers, itemized details, and print-to-PDF export functionality.

### Events
- Full CRUD management.
- Track event budget (allocated vs. used).
- Assign volunteers to specific events.

### Programs
- Full CRUD management.
- Create relief programs with start and end dates.
- Link sponsors (donors) to the programs.

### General Platform Features
- **Model Relationships:** Utilizes `ForeignKey` (e.g., Donation linked to Donor, Program sponsor linked to Donor) and `ManyToMany` (e.g., Event assigned to Volunteers).
- **Search & Pagination:** Search functionality (by name, email, or donor) and pagination (5 records per page) available on all list pages.
- **Live Homepage Dashboard:** Displays real-time statistics including total donors, total volunteers, total events, active programs, total money raised, total donations made, and total volunteer hours. These stats are calculated dynamically using Django aggregation queries.
- **Responsive Design:** Clean and accessible interface built with Bootstrap 5. Includes a mobile-friendly navbar with a collapsible hamburger menu and a responsive footer containing NGO contact details.
- **Django Admin Panel:** Full CRUD management accessible via the built-in Django Admin interface for bulk data management, conveniently linked directly from the site navbar.

## Project Structure

The project is divided into the following 5 apps:
- `donors`: Handles donor profiles and information.
- `volunteers`: Manages volunteer profiles and their contributed hours.
- `donations`: Records and manages all donations and links them to donors.
- `events`: Organizes events, budgets, and volunteer assignments.
- `programs`: Tracks various NGO relief programs and their sponsors.

## How Email Notifications Work

The platform includes an email notification system that automatically sends a thank-you email to donors when a new donation is recorded.

**For Development (Current Setup):** 
The system currently uses Django's console email backend for demonstration purposes. Emails are not actually sent over the internet; instead, the email content is printed directly to the server terminal/console, and a success message is displayed on the webpage.

**For Production:**
To send real emails, you will need to switch to an SMTP backend by updating `settings.py` with actual email provider credentials (e.g., Gmail, SendGrid, Amazon SES):
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.example.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your_email@example.com'
EMAIL_HOST_PASSWORD = 'your_password'
```

## Installation / Setup

To run this project locally, follow these steps:

### 1. Clone the repository
```bash
git clone <your-repository-url>
cd HopeBridge
```

### 2. Create and activate a virtual environment
```bash
python -m venv env
# On Windows:
env\Scripts\activate
# On Mac/Linux:
source env/bin/activate
```

### 3. Install dependencies
```bash
pip install django
```

### 4. Run migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create a superuser
```bash
python manage.py createsuperuser
```
> **Note:** Admin login credentials should be created locally using the command above. For security reasons, do **not** hardcode or share your admin username and password in this file or anywhere else in the repository.

### 6. Run the server
```bash
python manage.py runserver
```

### 7. Access the application
- Main Site: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- Django Admin Panel: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

## Future Improvements

While this portal is fully functional, there are several ways it could be expanded in the future:
- **User Authentication:** Allow donors and volunteers to create accounts, log in, and view their own profiles and history.
- **Real SMTP Email Integration:** Replace the console backend with a live email service for production.
- **Role-Based Access Control:** Add different permission levels for staff, volunteers, and donors.
- **PDF Export via Python:** Generate PDFs directly on the server (using libraries like `WeasyPrint` or `ReportLab`) instead of relying on the browser's print function.
- **REST API:** Build a RESTful API using Django Rest Framework (DRF) to serve data to mobile apps or front-end frameworks like React/Vue.
