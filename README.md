# Moment ⏳ — Time Management Web Application

[![Live Demo](https://img.shields.io/badge/Live%20Site-Moment.aranyait.com.bd-brightgreen)](https://moment.aranyait.com.bd)
[![Built With Django](https://img.shields.io/badge/Built%20with-Django-blue)](https://www.djangoproject.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

**Moment** is a full-featured solo-built full-stack time management web application. It helps users create productive routines, manage one-time and recurring tasks, reflect on their progress, and view analytics based on their time usage.

---

## 🔥 Live Website

🌐 Visit the live app at: [https://moment.aranyait.com.bd](https://moment.aranyait.com.bd)

Users can create an account and start managing their time instantly.

---

## 🚀 Features

- 🏠 **Landing Page**
- 📜 **Feature Overview**
- 💰 **Pricing Page**
- 🔐 **Authentication System**
  - Sign Up / Log In
  - Google Sign-In
  - Forgot Password / Reset Password
  - Profile Update
- 🗓 **Routine Management**
  - Create / Edit / Delete Routine Templates
  - Reflect on completed routines
- ✅ **Task Management**
  - Create / Read / Update / Delete One-time and Recurring Tasks
- 📊 **Analytics Dashboard**
  - Visual insights on time usage and routines

---

## 🛠 Tech Stack

### Frontend
- HTML5, CSS3
- Bootstrap 5
- JavaScript (ES6)
- jQuery

### Backend
- Python 3
- Django
- Django REST Framework

### DevOps & Deployment
- Hosted on a WSGI server (due to ASGI limitations)
- Pipenv for dependency management
- Cron Jobs for scheduled task updates
- Environment variables managed with `python-dotenv`
- SMTP email support for authentication and notifications

---

## ⚙️ Environment Variables (`.env`)

Create a `.env` file in the root of the project and populate it with the following keys:

```env
# Django Settings
SECRET_KEY=
DEBUG=
ALLOWED_HOSTS=

# Email Settings
EMAIL_HOST=
EMAIL_PORT=
EMAIL_USE_SSL=         # Typically True if using port 465
EMAIL_USE_TLS=
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
DEFAULT_FROM_EMAIL=
DEFAULT_FROM_NAME=

# CSRF Settings
CSRF_TRUSTED_ORIGINS=

# Security Settings
SECURE_SSL_REDIRECT=0
SESSION_COOKIE_SECURE=0
CSRF_COOKIE_SECURE=0

# Static Files
STATIC_URL=static/
STATIC_ROOT=staticfiles/
USE_WHITENOISE=False

# Admin URL
ADMIN_URL=admin/

# Optional DB Configs (if using a different DB engine)
# DB_ENGINE=
# DB_NAME=
# DB_USER=
# DB_PASSWORD=
# DB_HOST=
# DB_PORT=
```


## 📦 Local Development Setup

Follow these steps to set up and run the project locally:

### 1. Clone the Repository

```bash
git clone https://github.com/salmanshovon/moment-django.git
cd moment-django
```

### 2. Set Up the Virtual Environment Using Pipenv

```bash
pipenv install
pipenv shell
```

### 3. Configure Environment Variables

Create a `.env` file in the root directory and populate it using the template provided in the [Environment Variables](#️environment-variables-env) section above.

### 4. Apply Database Migrations

```bash
python manage.py migrate
```

### 5. Run the Development Server

```bash
python manage.py runserver
```

---

## 🧩 Notable Decisions & Architecture Choices

- **No Celery/Redis**: Due to the WSGI-only support on the production server, asynchronous task scheduling (like routine checks and updates) is handled via **cron jobs** instead of Celery with Redis.
- **WSGI Deployment**: The application is deployed using **WSGI**, ensuring compatibility with the current shared hosting infrastructure.
- **Progressive Web App (PWA)**: Fully implemented with installable experience on supported mobile browsers.
- **Environment-based Security Configs**: SSL redirect settings, secure cookies, and CSRF protection are all **configured via environment variables** to support both development and production needs seamlessly.

---

## 📈 Future Enhancements

- ✅ Switch to **ASGI deployment** to support Celery and Redis for real-time processing
- 📊 Add more **detailed analytics and personalized insights**
- 📆 Implement **calendar view** for enhanced task scheduling and overview

---

## 🧑‍💻 Author

**Salman Mahmood**

- 🔗 [GitHub Profile](https://github.com/salmanshovon)  
- 🌐 [Live Site: moment.aranyait.com.bd](https://moment.aranyait.com.bd)

---

## 📝 License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for full details.

---

## 🙌 Contributions

This project is developed and maintained solo, but contributions, suggestions, and feedback are welcome!

- 🛠 Fork the repository  
- 🐞 Submit issues for bugs or feature requests  
- 📬 Open a pull request with improvements

