# 🎮 Raja–Mantri–Chor–Sipahi | Django REST API

A complete backend implementation of the traditional Indian game  
**Raja–Mantri–Chor–Sipahi**, built using **Django** and **Django REST Framework**.

This project focuses on clean API design, proper game-state handling, secure UUID-based
identification, and realistic game logic — making it ideal for backend assignments,
learning REST APIs, and interview demonstrations.

---

## ✨ Features

- Create game rooms with unique UUIDs
- Join players (maximum 4 per room)
- Automatic random role assignment:
  - Raja
  - Mantri
  - Sipahi
  - Chor
- Private role reveal per player
- Mantri guessing logic (guess the Chor)
- Accurate scoring rules:
  - Raja → 1000 points  
  - Mantri → 800 points  
  - Sipahi → 500 points  
  - Chor → 0 points (steals Mantri’s points on wrong guess)
- Round result & leaderboard APIs
- Robust validation & error handling
- Clean, RESTful architecture

---

## 🧱 Tech Stack

- **Python 3.9+**
- **Django**
- **Django REST Framework**
- **SQLite** (development-friendly, easily switchable to MySQL/PostgreSQL)

---

## ⚙️ Installation & Setup
```bash
### 1️⃣ Clone the repository

git clone <your-repository-url>
cd rmc_project

### 2️⃣ Create & activate virtual environment
python3 -m venv venv
source venv/bin/activate        # macOS / Linux
venv\Scripts\activate.bat     # Windows

###3️⃣ Install dependencies
pip install django djangorestframework


###4️⃣ Run database migrations
python manage.py makemigrations
python manage.py migrate

###5️⃣ Start the development server
python manage.py runserver
```
