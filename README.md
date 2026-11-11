# ReadApp - Adaptive Reading & Quiz Assessment Platform

A web application built with **Flask** and **MySQL** designed to help students improve their reading comprehension through targeted passages, interactive quizzes, audio recording evaluations, and gamified content. The app features personalized passage recommendations based on **CEFR language levels** and **age categories**, integrated payment support via **Chapa**, and an admin evaluation portal.

---

## 🚀 Features

### 👨‍🎓 Student Portal
- **User Authentication:** Secure signup/login with hashed passwords and session management.
- **Adaptive Passage Delivery:** Dynamically fetches reading passages tailored to the student's **CEFR Level** (`A1`–`C2`) and **Age Group** (`3-6`, `7-12`, `13-19`, `20+`).
- **Audio Reading Submission:** Allows students to record and submit their oral reading performance for administrator feedback.
- **Interactive Quizzes:** Dynamic quiz consumption per reading passage.
- **Subscription & Payment:** Integrated with **Chapa Payment API** to handle monthly subscriptions and track subscription expiry.
- **Gamified Learning:** Access to interactive learning games (*Forest Readers*, *Story Quest*).

### 👨‍💼 Admin Portal
- **Passage Management:** Create, view, and delete reading passages categorized by target CEFR level and age group.
- **Quiz Creator:** Attach JSON-formatted quizzes to specific reading passages.
- **Audio Evaluation & Feedback:** Review student audio recordings alongside original passage texts and provide direct performance feedback.

---

## 🛠️ Tech Stack

- **Backend:** Python 3, Flask (Blueprints, Sessions, Wraps)
- **Database:** MySQL (PyMySQL driver)
- **Payment Gateway:** Chapa API (`chapa_utils`)
- **Security:** Werkzeug Password Hashing (`generate_password_hash`, `check_password_hash`)
- **AI Integration Support:** Google Gemini API module (`gemini.py`)
- **Timezone Management:** `pytz` (configured for Africa/Addis_Ababa)

---

## 📁 Project Structure

```text
.
├── admin.py           # Admin blueprint (Passage management, evaluation, quizzes)
├── student.py         # Student blueprint (Authentication, payments, passage reading)
├── schema.sql         # Database schema initialization script
├── gemini.py          # Google Gemini AI utility wrapper
├── chapa_utils.py     # Chapa payment processing utilities
└── static/            # Audio upload storage and static assets
```

---

## 🗄️ Database Setup

Import the provided `schema.sql` into your MySQL instance:

```bash
mysql -u root -p < schema.sql
```

### Database Tables:
1. **`students`**: Stores user profiles, hashed credentials, CEFR level, birthdate, and payment expiration dates (`paiduntil`).
2. **`passages`**: Contains reading texts indexed by title, text body, CEFR level, and age group.
3. **`quizzes`**: Stores JSON-encoded quiz questions linked to passages (`ON DELETE CASCADE`).
4. **`audiorec`**: Tracks uploaded student audio recordings and admin feedback (`ON DELETE CASCADE`).

---

## ⚡ Setup & Installation

### 1. Prerequisites
- Python 3.8+
- MySQL Server

### 2. Install Dependencies
```bash
pip install flask pymysql python-dotenv werkzeug pytz
```

### 3. Environment Variables
Create a `.env` file in the project root:

```env
admin=your_admin_username
password=your_admin_password
CHAPA_SECRET_KEY=your_chapa_secret_key
```

### 4. Database Connection Configuration
Ensure the MySQL credentials in `admin.py` and `student.py` match your local setup:

```python
pymysql.connect(
    host='localhost',
    database='readdb',
    user='root',
    password='YOUR_DATABASE_PASSWORD'
)
```

### 5. Run the Application
```bash
python app.py
```

Access the application in your browser:
- **Student Portal:** `http://127.0.0.1:5000/student`
- **Admin Portal:** `http://127.0.0.1:5000/admin`

---

## 🔒 Security & Route Protection

The app includes two custom Flask decorators for authorization:
- **`login_required`**: Restricts access to authenticated student or admin sessions.
- **`payment_required`**: Ensures students have an active paid subscription (`paiduntil >= current_date`) before accessing reading passages, audio recording features, or quizzes.

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for details.
