# Medlocker - Medical Record Management System

A Django-based web application for managing medical records securely. Medlocker allows doctors and patients to interact, share, and store medical information in a centralized, secure platform.

## Project Overview

Medlocker is a healthcare platform that bridges the gap between doctors and patients by providing:
- **Secure Authentication**: Separate registration and login for doctors and patients
- **Medical Records Management**: Upload, store, and retrieve patient medical records
- **Role-Based Dashboard**: Different interfaces for doctors and patients
- **Patient Profiles**: Store patient information including blood group and emergency contacts
- **Profile Pictures**: User profile photo support
- **Doctor-Patient Interaction**: Doctors can view and manage patient records

## Features

- 👨‍⚕️ **Doctor Dashboard**: View assigned patients and their medical records
- 👤 **Patient Dashboard**: Manage personal health records and upload documents
- 📋 **Medical Records**: Upload and manage patient medical documents
- 👥 **User Profiles**: Store blood group, emergency contacts, and profile pictures
- 🔐 **Secure Authentication**: Role-based user authentication for doctors and patients
- ⚙️ **Settings Management**: User-specific settings and preferences

## Tech Stack

- **Backend**: Django (Python)
- **Database**: SQLite (default) / PostgreSQL (configurable)
- **Frontend**: HTML, CSS, JavaScript
- **Static Files**: CSS, Images
- **Media Storage**: Local file system

## Project Structure

```
Medlocker/
├── manage.py                 # Django management script
├── requirements.txt          # Python dependencies
├── core/                     # Main application
│   ├── models.py            # Database models
│   ├── views.py             # View logic
│   ├── forms.py             # Form definitions
│   ├── urls.py              # URL routing
│   ├── admin.py             # Admin interface
│   ├── middleware.py        # Custom middleware
│   ├── decorators.py        # Custom decorators
│   ├── migrations/          # Database migrations
│   ├── templates/           # HTML templates
│   │   ├── auth/           # Login & registration templates
│   │   ├── doctor/         # Doctor-specific templates
│   │   ├── patient/        # Patient-specific templates
│   │   └── admin/          # Admin templates
│   └── static/             # CSS and static files
├── medtrack_project/        # Django project configuration
│   ├── settings.py         # Project settings
│   ├── urls.py             # Main URL routing
│   ├── wsgi.py             # WSGI configuration
│   └── asgi.py             # ASGI configuration
└── media/                   # User-uploaded files
    ├── patient_*/          # Patient-specific records
    └── profile_pics/       # User profile pictures
```

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (recommended)

### Setup Instructions

1. **Clone the repository**
   ```bash
   cd Medlocker
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Apply database migrations**
   ```bash
   python manage.py migrate
   ```

5. **Create a superuser (admin account)**
   ```bash
   python manage.py createsuperuser
   ```

6. **Collect static files**
   ```bash
   python manage.py collectstatic
   ```

## Running the Application

### Development Server

```bash
python manage.py runserver
```

The application will be available at `http://localhost:8000`

### Access Points

- **Home/Admin**: http://localhost:8000/admin
- **Login**: http://localhost:8000/auth/login
- **Patient Registration**: http://localhost:8000/auth/register/patient
- **Doctor Registration**: http://localhost:8000/auth/register/doctor

## Authentication

### Patient Registration
- Users register as patients to upload and manage their medical records
- Profile includes blood type, emergency contact, and profile picture

### Doctor Registration
- Licensed professionals register as doctors
- Access to view assigned patient records
- Can manage patient medical information

## Database Models

The application includes models for:
- **User**: Extended user model with role-based access
- **UserInfo**: Patient information (blood group, emergency contact, profile picture)
- **Medical Records**: Patient document storage
- **Doctor-Patient Relationships**: Link between doctors and their patients

## Configuration

Edit `medtrack_project/settings.py` to configure:
- Database settings
- Allowed hosts
- Static and media file paths
- Email configuration
- Security settings

## API Endpoints & Routes

Refer to `core/urls.py` for detailed URL routing configuration.

## Deployment

For production deployment:
1. Set `DEBUG = False` in settings.py
2. Configure a production database (PostgreSQL recommended)
3. Set up a web server (Gunicorn, uWSGI)
4. Configure a reverse proxy (Nginx)
5. Enable HTTPS and secure headers
6. Store media files in cloud storage (AWS S3, Azure Blob)

## Security Considerations

- ✅ Use strong SECRET_KEY in production
- ✅ Enable CSRF protection
- ✅ Use HTTPS in production
- ✅ Implement proper access controls
- ✅ Sanitize user inputs
- ✅ Secure media file access

## Contributing

1. Create a feature branch
2. Make your changes
3. Write/update tests
4. Submit a pull request

## License

This project is private and proprietary. All rights reserved.

## Support

For issues, questions, or suggestions, please contact the development team.

---

**Last Updated**: 2026-08-14
