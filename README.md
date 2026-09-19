# Library Service API 📚

Library Service API is a RESTful web service built with Django REST Framework (DRF) designed for managing library
operations, automated book borrowings, payment processing via Stripe, and real-time Telegram notifications.

## 🚀 Key Features

* **Advanced JWT Authentication:**
    * Email-based user identification (without `username`).
    * Secure access and refresh token management using `djangorestframework-simplejwt`.
* **Book & Inventory Management:**
    * Full CRUD operations for books with titles, authors, covers (HARD/SOFT), daily fees, and inventory tracking.
    * Automatic inventory deduction upon borrowing and restock upon return.
* **Borrowing Management:**
    * Borrowing creation with strict inventory checks (prevents borrowing if inventory is 0).
    * Dynamic tracking of active and overdue borrowings.
    * Atomic return handling with automatic recalculation of actual return dates.
* **Stripe Payment Processing:**
    * Seamless integration with Stripe Checkout for paying borrowing fees and overdue fines.
    * Real-time payment status verification (PENDING/PAID).
    * Automated fine calculation for late book returns.
* **Automated Telegram Notifications:**
    * Instant Telegram alerts sent to a specified channel/chat when new borrowings are created.
    * Asynchronous daily checks via **Celery & Redis** to identify and notify about overdue borrowings.
* **Role-Based Access Control (RBAC):** Custom permissions ensuring regular users can only manage their own borrowings
  and payments, while administrators have full access to all system resources.
* **Interactive API Documentation:** Integrated OpenAPI documentation generated via `drf-spectacular` (Swagger UI &
  ReDoc).
* **High Code Quality & Testing:**
    * Strict adherence to **PEP 8** standards verified with `flake8`.
    * Comprehensive test suite reaching **94% total code coverage** (measured via `coverage`).

---

## 🛠️ Tech Stack

* **Core Framework:** Python, Django 5, Django REST Framework
* **Authentication:** SimpleJWT (JWT Tokens)
* **Database:** PostgreSQL
* **Asynchronous Tasks & Scheduling:** Celery, Redis
* **Third-Party Integrations:** Stripe API, Telegram Bot API
* **Documentation & OpenAPI:** `drf-spectacular` (Swagger & ReDoc)
* **Testing & Code Quality:** Django TestCase, `coverage` (94%), `flake8` (PEP 8)
* **Containerization:** Docker & Docker Compose

---

## 📁 Project Structure

```text
├── books/               # Book inventory & catalog management
├── borrowings/          # Borrowing creation, return logic & status tracking
├── library_service/     # Main project configuration (settings, Celery, URLs)
├── notifications/       # Telegram Bot integration & messaging helpers
├── payments/            # Stripe integration, session management & fine calculation
├── users/               # Custom User model & JWT authentication
├── .flake8              # Flake8 linter configuration
├── Dockerfile           # App container configuration
├── docker-compose.yaml  # Multi-container orchestration (App, DB, Redis, Celery)
└── requirements.txt     # Python dependencies
```

---

## 🔧 Getting Started & Installation

### Prerequisites

Make sure you have the following installed on your system:

* [Docker Desktop](https://www.docker.com/products/docker-desktop/) (including Docker Compose)
* [Git](https://git-scm.com/)

---

1. **Clone the repository:**
   ```bash
   git clone https://github.com/SerhiiAm/Library-Service.git
   cd Library-Service
   ```

2. **Configure Environment Variables:**
   Create a `.env` file in the root directory and define your variables:
   ```env
   POSTGRES_HOST=db
   POSTGRES_PORT=5432
   POSTGRES_DB=library_service
   POSTGRES_USER=library_service
   POSTGRES_PASSWORD=library_service
   DEBUG=True
   TAG=v1.0.0
   SECRET_KEY=your_django_secret_key_here
   STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
   FINE_MULTIPLIER=2
   CELERY_BROKER_URL=redis://redis:6379
   CELERY_RESULT_BACKEND=redis://redis:6379/0
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
   TELEGRAM_CHAT_ID=your_telegram_chat_id_here
   ```

3. **Build and Run the Containers:**
   Start the application and PostgreSQL database:
   ```bash
   docker compose up --build
   ```

4. **Create a Superuser (Admin):**
   To access the Django Admin or manage system resources:
   ```bash
   docker compose exec app python manage.py createsuperuser
   ```

5. **Testing & Code Quality:**

   **Running Unit Tests & Coverage Report**  
   To run all automated tests and verify test coverage (94%):
   ```bash
   docker compose exec app coverage run --source='.' manage.py test
   docker compose exec app coverage report
   