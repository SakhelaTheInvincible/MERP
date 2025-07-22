# Magic Events - Event Registration Platform

An event registration platform built with Django and Django REST Framework that allows customers to register for events and manage their bookings.

## Features

### Core Functionality
- **Event Creation**: Create events with title, start/end dates, thumbnails, and descriptions
- **Event Management**: Full CRUD operations for events
- **User Registration**: Self-service registration for events
- **Profile Management**: View/Update user profile
- **Management Codes**: Unique codes for registration management
- **Cancellation Logic**: Business rules for event cancellation
- **REST API**: Complete API for frontend integration
- **Web Interface**: Modern, responsive UI for event creation, browsing, and registration

### Business Rules
- Clients receive a unique management code after registration
- Cancellation is only allowed for:
  - Events lasting no longer than 2 days
  - At least 2 days before the event start date
- One registration per email per event

## Technology Stack

- **Backend**: Django 4.2.7, Django REST Framework 3.14.0
- **Database**: SQLite (easily replaceable with PostgreSQL/MySQL)
- **Frontend**: Bootstrap 5, jQuery, Font Awesome
- **Image Handling**: Pillow for thumbnail processing

## Quick Start

### Prerequisites
- Python 3.8+
- pip

### Installation

1. **Clone/Download the project**
   ```bash
   git clone https://github.com/SakhelaTheInvincible/MERP.git
   cd MERP
   ```

2. **Run Setup**
   ```bash
   python setup.py
   ```

3. **Create Env**
   - Create .env file in root directory
   - copy code from env.example to .env
   - set up your email and password
   - (hint) your password must be app password 
   (example from gmail: https://security.google.com/settings/security/apppasswords)


4. **Start the server**
   ```bash
   python manage.py runserver
   ```

5. **Access the application**
   - Web Interface: http://127.0.0.1:8000/
   - API Root: http://127.0.0.1:8000/api/
   - Admin Panel: http://127.0.0.1:8000/admin/

## Project Structure

```
MERP/
├── magic_events/           # Django project settings
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── events/                 # Main application
│   ├── __init__.py
│   ├── admin.py           # Admin interface configuration
│   ├── apps.py
│   ├── models.py          # Event and Registration models
│   ├── serializers.py     # DRF serializers
│   ├── urls.py            # URL routing
│   └── views.py           # API and web views
├── accounts/              # user management
│   ├── __init__.py
│   ├── apps.py
│   ├── forms.py           # Manage form updates
│   ├── urls.py            # URL routing
│   └── views.py           # API and web views
├── templates/             # HTML templates
│   ├── base.html
│   └── events/
│       ├── events_list.html
│       ├── event_detail.html
│       └── registration_management.html
├── media/                 # User uploads (created automatically)
├── static/                # Static files (created automatically)
├── db.sqlite3             # Database (created automatically)
├── manage.py              # Django management script
├── setup.py               # Setup application
├── requirements.txt       # Python dependencies
└── README.md              # This file
```

## Admin Interface

Access the Django admin at `/admin/` to:
- Create and manage events
- View all registrations
- Monitor registration statistics
- Manage user accounts


### Cancellation Rules
The platform implements specific business rules for registration cancellation:

1. **Event Duration Check**: Only events lasting 2 days or less can be cancelled
2. **Advance Notice**: Cancellations must be made at least 2 days before event start
3. **Status Check**: Only active registrations can be cancelled

These rules are enforced both in the API and the web interface.