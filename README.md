# HireHub - Job Portal with Resume Builder 🧑‍💼💼

**HireHub** is a modular web application built to connect job seekers with employers and help users create professional resumes. The system now consists of two main components:

- A **Flask-based Job Portal API backend**
- A **Django-powered frontend** that consumes the Flask APIs and also hosts the **Resume Builder** app

---

## 🚀 Features

### 🧑‍💼 For Job Seekers:
- Register and create a user profile (handled via Flask backend)
- Browse and search for job listings
- Apply for jobs via API endpoints
- Build and download resumes using the integrated Django Resume Builder

### 🧑‍💼 For Employers:
- Register and manage company profile
- Post new job listings via Flask API

### 📄 Resume Builder (Django App):
- Choose from different resume templates
- Enter personal info, education, experience, skills, etc.
- Generate a professional PDF resume
- Option to print or download the resume

---

## 🛠️ Tech Stack

- **Backend (Job Portal)**: Flask (Python REST API)
- **Frontend**: Django (HTML, CSS, Tailwind, Bootstrap, DRF for API integration)
- **Resume Builder**: Django App using reportlab for PDF generation
- **Database**: SQLite (default for development)
- **Authentication**: Handled via Flask APIs

---

## 🔧 Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/HydraDocOc/HireHub-With-Resume-Builder-using-API.git
cd HireHub-With-Resume-Builder-using-API
```

---

### 2. Set Up Virtual Environment

```bash
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
```

---

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

> Note: Ensure both Flask and Django-related packages are included.

---

### 4. Run Flask Backend (Job Portal API)

```bash
cd FLASk   # Navigate to your Flask backend folder
python app.py
```

---

### 5. Run Django Frontend + Resume Builder

```bash
cd ../Django   # Navigate to Django frontend folder
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

Visit: [http://127.0.0.1:8000](http://127.0.0.1:8000)  
Ensure your Flask backend is also running at its default port (5000) for the APIs to be accessible.

---

## 📌 TODO / Future Enhancements

- Centralized admin dashboard for analytics
- Job recommendation engine (AI/ML based)
- More customizable resume templates
- Push/email notifications for job matches
- Dockerize the architecture for easier deployment

---

## 🚀📦✅🧑‍💻📤 Deployment
- Platform Used :- Pythonanywhere.com 
- Frontend (Django) Deployment link
  ```bash
  https:\\sanchal.pythonanywhere.com
  ```
- Backend (Flask) Deployment Link
  ```bash
  https:\\dhawalgoyal.pythonanywhere.com
  ```
- To Check Flask-Api use ```\api``` after the backend link and then access data . Ex:  ```https:\\dhawalgoyal.pythonanywhere.com\api\job\1 ```

---

## 🤝 Contributing

Contributions are welcome! Feel free to fork the repo and open a pull request with improvements, bug fixes, or new features.
