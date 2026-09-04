# FIELD ATLAS — SKILLING OUTCOMES PLATFORM

A production-grade, responsive skills and employment outcomes platform for India. Field Atlas connects training completion with longitudinal post-placement signal, providing tailored operational interfaces for **Trainers** and **Trainees**, 11-language localization (including dynamic RTL for Urdu), email OTP authentication, and real SQL persistence via Django 5+ and Django REST Framework.

---

## 1. Technology Stack

- **Frontend**: Pure HTML5, Vanilla CSS3, and Vanilla JavaScript (No React, TypeScript, Node.js, Vite, Express, or frontend frameworks).
- **Backend**: Python 3.12+ (tested on Python 3.14), Django 5+, Django REST Framework (DRF).
- **Database**: MySQL via PyMySQL driver with SQLite local development fallback.
- **Visualizations**: Chart.js for wage progression, cohort conversion funnel, provider benchmarking, and diagnostics.
- **Design Tokens & Icons**: Lucide Icons CDN, civic cartography palette (Deep Indigo, Field Teal, Indigo Blue, Ochre, Coral, Parchment).
- **Security**: 6-digit email OTP (10-min expiration, 3-attempt limit, 60s cooldown rate limiting), Django session/CSRF authentication, role-based authorization, and audit logging.

---

## 2. Key Features

### Role-Based Dashboards
1. **Trainer Dashboard (`/trainer/`)**:
   - **Overview**: Hero section, 5-step outcome route timeline (*Enrolled → Trained → Certified → Placed → Retained*), 4 metric KPI cards, Chart.js wage progression curve with baseline floor, cohort conversion funnel, provider pulse leaderboard, and non-placement donut chart.
   - **Follow-ups**: Priority assistance queue, WhatsApp and SMS message preview switcher with simulated typing state, response action tags, and live database persistence with consent verification.
   - **Trainees Directory**: Searchable, filterable table by provider, district, stage, and consent status. Full modal for enrolling new trainees and recording initial consent.
   - **Providers Benchmark**: Grouped bar chart comparing placement and retention, district insights (*"West Maharashtra is retaining talent longer"*), and employer validation stats.
   - **Reports**: Downloadable CSV exports for impact briefs, provider comparisons, and diagnostics, with automatic audit logging.

2. **Trainee Portal (`/trainee/`)**:
   - Mobile-first, streamlined learner dashboard.
   - Stage progress timeline rail (*Enrolled → Trained → Certified → Placed → Retained*).
   - Profile completion progress bar.
   - Current placement and verified wage record.
   - Upcoming check-in card with quick action buttons: *"I am working"*, *"I run my own business"*, *"I need support"*.
   - Consent management panel: Learners can grant or withdraw consent anytime.
   - Progress report download: Generates printable learner summary certificate.

3. **Editable Profile Page (`/profile/`)**:
   - Edit full name, phone number, preferred language, district, state, address, and professional bio.
   - Profile photo upload with instant preview.
   - Secure password change flow.

### 11-Language Localization
Native client and backend translations supporting:
1. English (`en`)
2. Hindi (`hi`)
3. Marathi (`mr`)
4. Bengali (`bn`)
5. Tamil (`ta`)
6. Telugu (`te`)
7. Kannada (`kn`)
8. Gujarati (`gu`)
9. Punjabi (`pa`)
10. Malayalam (`ml`)
11. Urdu (`ur`) — with automatic Right-to-Left (`dir="rtl"`) layout switching.

---

## 3. Local Setup & Execution Guide

### Prerequisites
- Python 3.12+ (or 3.14)
- Git / PowerShell / Terminal

### Step 1: Clone or Navigate to Directory
```bash
cd d:\vs
```

### Step 2: Install Python Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
copy .env.example .env
```
Default `.env` settings are already configured to use SQLite local fallback and console email backend (OTPs appear directly in the terminal).

### Step 4: Run Migrations
```bash
python manage.py makemigrations outcomes
python manage.py migrate
```

### Step 5: Seed Demo Records (Idempotent)
Populates initial demo accounts, trainees (Asha Devi, Ravi Kumar, Meena Kumari, Javed Ansari, Sonal Patil), placements, consents, and follow-ups:
```bash
python manage.py seed_demo_data
```

### Step 6: Start the Development Server
```bash
python manage.py runserver 127.0.0.1:8000
```
Open your browser at [http://127.0.0.1:8000/login/](http://127.0.0.1:8000/login/).

---

## 4. Default Demo Credentials

All demo accounts share the password: `Atlas@2026!`

| Role | Email | Field Atlas ID | Initial Landing View |
| :--- | :--- | :--- | :--- |
| **Trainer** | `trainer@fieldatlas.in` | `FA-TR-1001` | `/trainer/` (Trainer Dashboard) |
| **Trainee** | `trainee@fieldatlas.in` | `FA-24-0182` | `/trainee/` (Learner Portal) |
| **Admin** | `admin@fieldatlas.in` | `FA-AD-0001` | `/admin/` & `/trainer/` |

---

## 5. MySQL Configuration Instructions

To run on a production or local MySQL server:

1. Create a MySQL database and user:
```sql
CREATE DATABASE field_atlas CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'field_atlas_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON field_atlas.* TO 'field_atlas_user'@'localhost';
FLUSH PRIVILEGES;
```

2. Update `.env`:
```env
USE_MYSQL=True
DB_NAME=field_atlas
DB_USER=field_atlas_user
DB_PASSWORD=your_password
DB_HOST=127.0.0.1
DB_PORT=3306
```

3. Run migrations on MySQL:
```bash
python manage.py migrate
python manage.py seed_demo_data
```

*Note: PyMySQL is natively integrated in `backend/__init__.py`, so no binary C-compiler (`mysqlclient`) is required.*

---

## 6. Complete REST API Contract

All REST JSON endpoints are prefixed with `/api/`:

### Authentication
- `POST /api/auth/register/` — Register trainer or trainee with optional OTP.
- `POST /api/auth/login/` — Authenticate via email or Field Atlas ID + password.
- `POST /api/auth/logout/` — End session.
- `POST /api/auth/send-otp/` — Send 6-digit email OTP (rate-limited to 60s).
- `POST /api/auth/verify-otp/` — Verify OTP (max 3 attempts).
- `POST /api/auth/password-reset/` — Reset password with OTP.
- `POST /api/auth/change-password/` — Change password for logged-in user.
- `GET /api/auth/me/` — Return current session user details and role.

### Profiles & Localization
- `GET /api/profile/` — Fetch current user profile.
- `PATCH /api/profile/` — Update user profile details.
- `POST /api/profile/photo/` — Upload profile photo.
- `GET /api/i18n/languages/` — List all 11 supported national languages.
- `POST /api/i18n/set-language/` — Set preferred language.

### Trainer Operations
- `GET /api/trainer/dashboard/` — Aggregated KPI metrics, funnel, wage curve, and provider pulse.
- `GET /api/outcomes/trainees/` — Query trainees with search and filter parameters.
- `POST /api/outcomes/trainees/` — Create a new trainee record.
- `PATCH /api/outcomes/trainees/<id>/` — Update trainee record.
- `POST /api/outcomes/trainees/seed-demo/` — Seed demo trainees idempotently.
- `GET /api/outcomes/follow-ups/` — List priority follow-up queue.
- `POST /api/outcomes/follow-ups/` — Create a follow-up item.
- `POST /api/outcomes/follow-ups/seed-demo/` — Seed demo follow-up queue.
- `POST /api/outcomes/follow-ups/<id>/send/` — Dispatch outreach attempt (enforces active consent, increments attempts, updates DB).
- `GET /api/outcomes/placements/?trainee_id=<id>` — Placements list.
- `POST /api/outcomes/placements/` — Create placement.
- `POST /api/outcomes/consents/` — Grant or withdraw consent.
- `GET /api/reports/provider-export/` — Download provider performance CSV.
- `GET /api/reports/impact-export/` — Download consent-filtered impact brief CSV.

### Trainee Self-Service
- `GET /api/trainee/me/dashboard/` — Personal timeline, placement status, and upcoming check-in.
- `GET /api/trainee/me/profile/` & `PATCH /api/trainee/me/profile/` — Trainee profile.
- `GET /api/trainee/me/follow-ups/` — Trainee follow-up history.
- `POST /api/trainee/me/follow-ups/<id>/respond/` — Submit check-in update (*"working"*, *"own_work"*, *"need_help"*).
- `GET /api/trainee/me/progress-report/` — Structured learner progress summary.
- `GET /api/trainee/me/consent/` & `POST /api/trainee/me/consent/` — Manage personal consent status.

---

## 7. Testing & Verification

Run the automated test suite:
```bash
python manage.py test outcomes
```

### Test Results
```
Ran 11 tests in 8.903s

OK
```
Covering:
- User registration and role redirects (blocking unauthorized admin self-registration)
- 6-digit email OTP generation, expiry, and attempt limits
- Profile editing and field validation
- Trainee vs Trainer role permission isolation (HTTP 403 enforcement)
- Trainee enrollment with automatic consent recording
- Idempotent demo data seeding
- Consent grant and withdrawal
- Follow-up outreach dispatch with consent blocking
- Trainee check-in response behavior and stage advancement
- Placement filtering by trainee ID

---

## 8. Intentional Functional Limitations

1. **Email Service**: Defaults to Django Console Email Backend (`EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend`) for local development so 6-digit OTPs display cleanly in the terminal. For production, configure standard SMTP credentials in `.env` (`EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_USE_TLS`).
2. **SMS & WhatsApp Gateway**: Outreach actions are explicitly tagged as simulated/demo. In accordance with the prompt, no real SMS or WhatsApp messages are sent without external gateway credentials (e.g. Twilio / Gupshup).
3. **Aadhaar Privacy**: In strict compliance with civic cartography principles, raw Aadhaar numbers are never collected or stored; only pseudonymous Unified IDs are utilized.
