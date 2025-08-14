# Code-Spray

**Code-Spray** is an online code judge platform built using **Django**, designed for learning, experimentation, and full-stack development practice. It supports multiple programming languages, provides problem management tools, automated judging, and integrates **AI-powered feedback** through the **Google Gemini LLM API** for personalized code reviews and contextual hints.

**Live Demo**: [Code-Spray on Render](https://code-spray.onrender.com)

## Table of Contents

- [Features](#features)
- [AI Features: Google Gemini LLM Integration](#ai-features-google-gemini-llm-integration)
- [Getting Started](#getting-started)
- [Project Structure](#project-structure)
- [Core Modules and Design](#core-modules-and-design)
- [How It Works](#how-it-works)
- [Technologies Used](#technologies-used)
- [Contributing](#contributing)
- [Acknowledgements](#acknowledgements)

## Features

- **Multi-language Support**: Judge code submissions in C, C++, Java, and Python.
- **Problem Management**: Add, edit, and remove coding problems with test cases via the admin dashboard.
- **User Authentication**: Secure sign-up, login, and logout functionality.
- **Automated Judging**: Compile, run, and evaluate submissions against sample and hidden test cases.
- **Admin Dashboard**: Manage users, problems, and judging through Django’s built-in admin tools.
- **Deployment Ready**: Supports Docker and Render deployment configurations.
- **Database Integration**: Uses SQLite for development (configurable for PostgreSQL/MySQL in production).
- **AI Assistance**: Provides instant AI-powered code reviews and problem hints via Google Gemini LLM.

## AI Features: Google Gemini LLM Integration

The integration of **Google Gemini LLM** enhances **Code-Spray** by offering AI-powered assistance to help programmers improve their code and learn more effectively.

### Key AI Enhancements

- **Automated Code Reviews**:
  - Reviews code for **correctness, efficiency, and style**.
  - Identifies common errors and suggests targeted solutions.
  - Provides optimization suggestions with detailed explanations.
- **Instant, Contextual Hints**:
  - Offers problem-specific hints tailored to the user’s current progress.
  - Guides users toward solutions without revealing full answers.
  - Adapts hints based on user submissions and attempts.
- **Seamless Integration**:
  - Securely stores Gemini API key (never exposed to clients).
  - Handles requests asynchronously for a smooth user experience.
  - Implements rate-limiting for stable performance.

### Benefits for Learners

- **Faster Iteration**: Immediate AI-generated feedback accelerates the learning process.
- **Deeper Understanding**: Explanations tailored to the problem domain enhance comprehension.
- **Guided Learning Path**: Adaptive hints based on user progress foster better problem-solving skills.

## Getting Started

### Prerequisites

- Python 3.8+ with pip
- Git
- Docker & Docker Compose (optional for containerized setup)

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/siddharth-sekhar/Code-Spray.git
   cd Code-Spray
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
   Or, with Docker:
   ```bash
   docker-compose up --build
   ```

3. **Apply database migrations**:
   ```bash
   python manage.py migrate
   ```

4. **Run the development server**:
   ```bash
   python manage.py runserver
   ```

## Project Structure

| Directory / File           | Purpose                                              |
|----------------------------|------------------------------------------------------|
| `OnlineJudgeProject/`      | Django project configuration and URLs                |
| `users/`                   | User authentication and role management              |
| `problems/`                | Coding problems, test cases, and judging logic       |
| `static/`, `staticfiles/`  | CSS, JavaScript, and images (e.g., `FULL-LOGO.jpg`)  |
| `templates/`               | HTML templates for views                             |
| `requirements.txt`         | Python dependencies                                  |
| `docker-compose.yml`       | Docker multi-service configuration                   |
| `Dockerfile`               | Docker image build instructions                      |
| `entrypoint.sh`            | Script for starting container services               |
| `Procfile`                 | Deployment configuration for cloud services          |
| `render.yaml`              | Render.com deployment configuration                  |

## Core Modules and Design

1. **OnlineJudgeProject/**: Core Django settings, routing, and WSGI/ASGI configuration.
2. **users/**: Handles registration, login/logout, and profile management.
3. **problems/**: Manages CRUD operations for problems, test case associations, and judging logic.
4. **Static & Templates**: Frontend presentation layer with forms, layouts, and dashboard UI.
5. **Judging Logic**: Executes submissions in isolated environments and evaluates outputs.

## How It Works

1. Users sign up or log in to the platform.
2. Users select a coding problem from the available list.
3. Code is submitted via the web-based IDE.
4. **AI Hook** (optional): Users can request AI-powered feedback or hints from Gemini LLM.
5. Submissions are compiled, executed, and compared against expected outputs.
6. Verdict and AI-generated feedback are displayed to the user.
7. Admins can manage problems and test cases via the admin dashboard.

## Technologies Used

- **Backend**: Django, Python
- **Frontend**: HTML, CSS, JavaScript
- **Database**: SQLite (development), PostgreSQL/MySQL (production)
- **AI**: Google Gemini LLM API
- **Containerization**: Docker, Docker Compose
- **Deployment**: Render, Heroku (via `Procfile`)

## Contributing

**Code-Spray** is a personal development and learning project by Siddharth Sekhar. Contributions are welcome! To contribute:

1. Fork the repository.
2. Create a feature branch:
   ```bash
   git checkout -b feature/my-feature
   ```
3. Commit your changes and push:
   ```bash
   git push origin feature/my-feature
   ```
4. Open a Pull Request on GitHub.

## Acknowledgements

- Inspired by online judge platforms like Codeforces, HackerRank, and LeetCode.
- Powered by **Google Gemini LLM** for AI-driven code reviews and hints.
- Thanks to the open-source community for tools and libraries used in this project.