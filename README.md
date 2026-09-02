# 🎓 StudyPilot – AI Study Planner

StudyPilot is an AI-powered academic study planner designed to help students manage their academic tasks and generate optimized daily and weekly study schedules.

The system uses **Heuristic Search and Hill Climbing** to prioritize and organize academic tasks based on deadlines, priority, difficulty, task type, required study hours, available study time, and workload balance.

---
👥 Project Team
Project: StudyPilot – AI Study Planner
Domain: Artificial Intelligence / Data Science
Algorithm: Heuristic Search + Hill Climbing
## 🚀 Features

### 📊 Academic Dashboard

- View total academic tasks
- View pending tasks
- View completed tasks
- View pending study hours
- Track overall completion rate
- View upcoming deadlines
- Identify overdue and urgent tasks

### 📅 Daily Study Planner

- Displays classes scheduled for the selected day
- Displays pending academic tasks
- Calculates available study periods
- Generates an optimized daily study schedule
- Uses Hill Climbing optimization
- Displays the optimization score
- Provides an explanation of the scheduling decisions

### 📆 Weekly Study Planner

- Generates a Monday–Friday study plan
- Distributes academic tasks across available study periods
- Considers available study time
- Balances workload across the week
- Allocates breaks between study sessions
- Displays weekly workload
- Calculates a weekly optimization score

### 📋 Task Management

Students can add and manage:

- Assignments
- Projects
- Homework
- Lab Work
- Assessments
- Semester Examinations

Each task contains:

- Task name
- Subject
- Task type
- Deadline
- Required study hours
- Priority
- Difficulty
- Completion status

Completed tasks are automatically excluded from future daily and weekly planning.

---

## 🧠 AI Optimization

StudyPilot uses **Heuristic Search and Hill Climbing** to optimize academic study schedules.

The scheduling heuristic considers:

- 🚨 Deadline urgency
- ⭐ Task priority
- 🧠 Task difficulty
- 📚 Task type
- ⏰ Required study hours
- 📍 Position of tasks in the schedule
- ⚖️ Workload balance
- ☕ Break allocation
- 📅 Available study time

### Hill Climbing Process

The system follows these steps:

1. Collect pending academic tasks.
2. Calculate heuristic values for the tasks.
3. Generate an initial task ordering.
4. Generate neighboring solutions by changing task positions.
5. Calculate the score of each neighboring solution.
6. Move to a better solution when available.
7. Continue until no better neighboring solution is found.
8. Return the optimized study schedule.

The optimization score is normalized between **0 and 100**.

A higher score represents a better schedule according to the defined optimization criteria.

---

## 🛠️ Technologies Used

- **Python**
- **Streamlit**
- **Pandas**
- **NumPy**
- **Heuristic Search**
- **Hill Climbing**
- **CSV Data Storage**

---

## 📁 Project Structure

```text
AI_Study_Planner/
│
├── app.py
│
├── ai/
│   ├── heuristic.py
│   ├── hill_climbing.py
│   └── weekly_planner.py
│
├── utils/
│   └── scheduler.py
│
├── data/
│   ├── timetable.csv
│   └── tasks.csv
│
├── requirements.txt
├── README.md
└── .gitignore
