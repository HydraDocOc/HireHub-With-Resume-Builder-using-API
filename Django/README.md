# HireHub - Job Portal with Resume Builder 🧑‍💼💼

HireHub is a Django-based web application that serves as a comprehensive job portal, connecting job seekers with employers. It also includes an integrated **Resume Builder** tool, allowing users to create professional resumes directly on the platform.

---

## 🚀 Features

### 🧑‍💼 For Job Seekers:
- Register and create a user profile
- Browse and search for job listings
- Apply for jobs
- Build and download resumes using the Resume Builder

### 🧑‍💼 For Employers:
- Register and manage company profile
- Post new job listings

### 📄 Resume Builder (Additional App):
- Choose from different templates 
- Fill in personal details, education, experience, skills, and more
- Generate a clean and professional PDF resume
- Print the resume page into a PDF

---

## 🛠️ Tech Stack

- **Backend**: Django (Python)
- **Frontend**: HTML, CSS, Bootstrap , Tailwind, CrispyFroms
- **Database**: SQLite (default Django DB)
- **PDF Generation**: reportlab
- **Authentication**: Django's built-in auth system

---



## Installation

1. **Clone the Repository**
```bash
git clone https://github.com/dikshaggarwal/hirehub.git
cd hirehub
```

2. **Create a Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
Cd 'Repository name'   # To go into the project folder
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

4. **Apply Migrations**
```bash
python manage.py makemigrations
python manage.py migrate
```

5. **Run Server**
```bash
python manage.py runserver
```
6. **Visit the App** Open your browser and go to http://127.0.0.1:8000/

---
## 📌 TODO / Future Enhancements

- Admin dashboard for analytics
- Job recommendation system using AI
- Resume templates customization
- Email notifications for job matches

---
## 🤝 Contributing

Contributions are welcome! If you have suggestions or want to improve the codebase, feel free to fork the repo and create a pull request.