# 🎉 Magic Events - Event Registration Platform

An event registration platform built with **Django** and **Django REST Framework** that allows customers to register for events and manage their bookings.

## 🎬 Demo

[![Magic Events Demo](https://img.youtube.com/vi/TwH9rnvydLk/maxresdefault.jpg)](https://www.youtube.com/watch?v=TwH9rnvydLk)

*👆 Click the image above to watch the full demonstration*

---

## ✨ Features

### ⚙️ Core Functionality

- 📝 **Event Creation**: Title, start/end dates, thumbnails, and descriptions
- 🧩 **Event Management**: Full CRUD support
- 👤 **User Registration**: Self-service signup with email verification
- 🧾 **Profile Management**: View/Update profile
- 🆔 **Management Codes**: Unique codes for registration lookup
- ❌ **Cancellation Logic**: Business rules enforced
- 🔌 **REST API**: Complete API for frontend
- 🌐 **Web Interface**: Responsive UI for browsing and registration

### 🔐 Authentication & Security

- ✉️ **Email Verification**: 6-digit verification codes
- ⚡ **Real-time Validation**: Live checks for username/email availability
- 📧 **Email Uniqueness**: Strict uniqueness enforced
- 🔒 **Session Management**: Secure verification handling
- 👥 **Enhanced User Creation**: First name, last name required

### 📬 Email Notification System

- ✅ **Registration Confirmations**: Auto emails with codes
- 🧾 **Verification Codes**: Styled HTML templates
- 📄 **Event Details**: Rich HTML content
- 📡 **SMTP Integration**: Gmail/App Password ready

### 🗂️ Advanced Registration Management

- 🔄 **Reactivation**: Restore cancelled registrations
- ⚡ **Quick Access**: View recent registrations instantly
- 🧠 **Enhanced Cancellation**: Smart logic, better UX
- 📊 **Dashboard**: Admin registration management

### 🛠️ Admin Interface Enhancements

- 👑 **Custom User Admin**: Clean, organized interface
- 🤭 **Registration Monitoring**: Search + filter tools
- 🔐 **Admin-only Features**: Restricted access
- 🧑‍💼 **User Management**: Full control over users

### 🔧 API Architecture

- 🧱 **ViewSet-based**: Modular DRF ViewSets
- 💃️ **Modular Design**: Separation of concerns
- 🌐 **Better URLs**: Clean endpoint structures
- 🛡️ **Permissions**: Role-based access

### 📏 Business Rules

- ✅ Users get unique management code after registration
- ✉️ Email verification is **mandatory**
- ❌ Cancellation allowed only if:
  - Event is **≤ 2 days**
  - Requested **≥ 2 days** before start
- 🧑 One registration per email per event
- 🔄 Cancelled registrations can be reactivated if event hasn't started

---

## 🧱 Technology Stack

- 🐍 **Backend**: Django 4.2.7, DRF 3.14.0
- 📓 **Database**: SQLite (easy to switch to PostgreSQL/MySQL)
- 🖼️ **Frontend**: Bootstrap 5, jQuery, Font Awesome
- 🖼️ **Image Handling**: Pillow
- 📧 **Email**: SMTP with HTML templates
- 🔐 **Authentication**: Session-based + email verification

---

## 🚀 Quick Start

### 📦 Prerequisites

- Python 3.8+
- pip

### 🛠️ Installation

1. **Clone the project**

   ```bash
   git clone https://github.com/SakhelaTheInvincible/MERP.git
   cd MERP
   ```

2. **Run Setup**

   ```bash
   python setup.py
   ```

   The setup script will:

   - Create virtual environment
   - Install dependencies
   - Run migrations
   - Optionally create superuser
   - Create required folders

3. **Create ENV**
   - Create .env file
   - Copy code from `.env.example` and paste it in `.env`
   - set up your email and password fields
   (hint) your password must be app password
     (e.g., from Gmail: [https://security.google.com/settings/security/apppasswords](https://security.google.com/settings/security/apppasswords))

4. **Start Development Server**

   ```bash
   python manage.py runserver
   ```

5. **Access App**

   - 🌍 Web: `http://127.0.0.1:8000/`
   - 🔗 API: `http://127.0.0.1:8000/api/`
   - 🔐 Admin: `http://127.0.0.1:8000/admin/`

---

## 🗂️ Project Structure

```
MERP/
├── magic_events/                         # 🚀 Django project settings
│   ├── settings.py                       # ⚙️ Main configuration
│   ├── urls.py                           # 🌐 Main URL routing
│   └── wsgi.py                           # 🔗 WSGI application
├── events/                               # 📅 Main events application
│   ├── admin.py                          # 🛠️ Admin interface config
│   ├── models.py                         # 📊 Event & Registration models
│   ├── serializers.py                    # 🔄 DRF serializers
│   └── views.py                          # 📱 API & web views
├── accounts/                             # 👤 User management & auth
│   ├── admin.py                          # 🛠️ Enhanced user admin
│   ├── forms.py                          # 📝 Custom forms (signup, profile)
│   └── views.py                          # 🔐 Auth, verification ViewSets
├── templates/                            # 🎨 HTML templates
│   ├── base.html                         # 📄 Base template layout
│   ├── accounts/                         # 🔐 Authentication templates
│   │   ├── login.html                    # 🚪 Login page
│   │   ├── signup.html                   # ✍️ Enhanced signup with verification
│   │   └── profile.html                  # 👤 User profile page
│   └── events/                           # 📅 Event templates
│       ├── events_list.html              # 📋 Events listing page
│       ├── event_detail.html             # 📖 Event details page
│       ├── event_create.html             # ➕ Event creation form
│       └── registration_management.html  # 🗂️ Registration dashboard
├── media/                                # 📁 User uploads (auto-created)
├── static/                               # 🎨 Static files (auto-created)
├── db.sqlite3                            # 💾 Database (auto-created)
├── manage.py                             # 🔧 Django management script
├── setup.py                              # 🛠️ Automated setup script
├── requirements.txt                      # 📦 Python dependencies
└── README.md                             # 📚 This documentation
```

---

## 📧 Email Configuration

The platform includes a comprehensive email notification system:

### ⚡ Setup Requirements

1. Gmail account with App Password enabled
2. Environment variables in `.env`:
   ```
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=your-app-password
   ```

### 📢 Email Features

- 🧲 **Verification Codes**: 6-digit codes
- ✅ **Registration Confirmations**: With event details
- 📅 **Professional Templates**: HTML email designs
- ⚠️ **Error Handling**: Graceful fallback on failure

---

## 📍 API Endpoints

### 🔐 Authentication & User Management

- `POST /accounts/auth/signup/` – Register with verification
- `POST /accounts/auth/login/` – Login
- `POST /accounts/verification/send-code/` – Send code
- `POST /accounts/verification/verify-code/` – Verify code
- `POST /accounts/validation/check-username/` – Check username
- `POST /accounts/validation/check-email/` – Check email
- `GET/PUT /accounts/profile/` – Manage profile

### 📅 Events & Registrations

- `GET  /api/events/` – List events
- `POST /api/events/` – Create event *(admin)*
- `GET  /api/events/{id}/` – Event details
- `POST /api/registrations/` – Register
- `GET  /api/registrations/my/` – My registrations
- `GET  /api/registrations/lookup/{code}/` – Lookup by code
- `POST /api/registrations/cancel/{code}/` – Cancel

---

## 👤 Admin Interface

Access Django Admin at `/admin/` to:

- ✍️ Manage events
- 📊 View/monitor registrations
- 🤝 Manage users
- 📈 View login stats and email verifications

### 🧑‍💼 Admin Features

- 👤 **Enhanced User Admin**
- 🔎 **Advanced Filtering**
- ⚖️ **Permission Controls**
- 📒 **Bulk Operations**

### 🔒 User Roles

- **Regular Users**: Register/manage own events
- **Staff/Admins**: Create/manage all data

### ⛔️ Cancellation Rules

1. ⏳ **Event Duration**: Must be ≤ 2 days
2. ⏰ **Advance Notice**: Cancel ≥ 2 days before event
3. 🔁 **Status Check**: Must be active

All rules enforced in **API** & **Web UI**.