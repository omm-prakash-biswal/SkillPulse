# FIELD ATLAS — SKILLPULSE BACKEND API SERVICE

A production-grade, secure Django 5+ and Django REST Framework (DRF) backend service for the Field Atlas / SkillPulse outcomes platform. This backend provides complete RESTful endpoints for trainer operations, trainee lifecycle management, cryptographic email OTP verification, longitudinal follow-ups, ReportLab verifiable PDF certificates, k-anonymity privacy safeguards, and real SQL persistence (MySQL / SQLite) with full CORS support for decoupled frontends.

> **Frontend Repository**: The decoupled web client is available at [priyanshu-pgb/SkillPulse-Frontend](https://github.com/priyanshu-pgb/SkillPulse-Frontend).

---

## 1. Technology Stack

- **Backend**: Python 3.12+ (verified on Python 3.14), Django 5+, Django REST Framework (DRF).
- **CORS Support**: `django-cors-headers` for seamless cross-origin communication with decoupled frontends (e.g., Vercel / Netlify).
- **Database**: MySQL via PyMySQL driver with SQLite local development fallback.
- **Visualizations**: Chart.js for wage progression, cohort conversion funnel, provider benchmarking, and diagnostics.
- **Certificates**: ReportLab 4.0+ for high-fidelity landscape PDF generation with cryptographic verification tokens and direct download links.
- **Design Tokens & Icons**: Lucide Icons CDN, civic cartography palette (Deep Indigo `#1E2749`, Field Teal `#0E8176`, Indigo Blue `#49618B`, Ochre `#D69541`, Coral `#D56F58`, Parchment `#F7F5F0`).
- **Security**: Cryptographically secure 6-digit email OTP via `secrets` module with HMAC-SHA256 digests, 10-minute expiration, single-use invalidation, anti-enumeration, 5-attempt temporary account lockout, password complexity rules, atomic transactions, and Pillow photo sanitization.

---

## 2. Key Architecture & Hardening Features

### Course Management & Trainee Lifecycle
1. **Course Creation & Publishing**: Trainers create courses with categories, student capacities, and duration. Publishing opens the course to the public catalog.
2. **Trainee Applications**: Trainees browse published offerings and submit applications with qualitative statements of motivation.
3. **Application Review & Enrollment**: Trainers review applicant rosters to approve or reject with decision notes; approvals automatically generate active student enrollments and notify learners.
4. **Progress & Roster Monitoring**: Trainers track student completion percentages, record completion notes, and monitor class capacity.
5. **Verifiable PDF Certificates**: Completed students receive tamper-evident landscape PDF certificates generated via ReportLab with unique verification UUIDs.
6. **Public Verification Portal**: Employers and verifiers can validate credentials at `/certificate/verify/<token>/` without requiring authentication.
7. **Employment Outcome Surveys**: Graduated trainees report employment status, employer name, job title, and monthly earnings; trainers verify reported data.
8. **k-Anonymity Privacy Safeguards**: Course wage metrics are concealed when fewer than 5 outcomes have been submitted (`< 5 responses`), displaying `"Wage data hidden to protect learner privacy (< 5 responses)"`.

### Trainer Data Isolation
- Strict row-level and object-level scoping: Trainers can only query, edit, reschedule, or outreach trainees assigned to them (`assigned_trainer`), and only manage courses they instruct.
- Accessing or modifying a participant or course outside the trainer's authorized scope immediately triggers an HTTP 403 Forbidden response.
- Admins retain unrestricted global visibility across all training partners and district hubs.
- Trainees are restricted strictly to their personal self-service learning portal, applications, and check-in timeline.

### In-App Notification System
- Real-time in-app alerts delivered to both trainers and trainees.
- Header notification bell with unread badge counter and popover drawer.
- Event categories: Course Applications, Approvals, Certificate Issuance, Outcome Survey Reminders, and General Alerts.

### Cryptographic OTP & Account Lockout
- **HMAC-SHA256 Storage**: Raw 6-digit OTP codes are never persisted in plain text. Stored records contain only HMAC digests keyed with the application secret.
- **Single-Use & Invalidation**: Used or expired codes are permanently invalidated.
- **Rate-Limiting**: 60-second cooldown per target email/IP address.
- **Mandatory Registration OTP**: Self-registration requires verified email ownership.
- **Temporary Account Lockout**: 5 consecutive failed login attempts automatically locks the account for 15 minutes.

### Longitudinal Follow-Up & Rescheduling Workflow
- Multi-milestone outreach tracking at 3, 6, and 12-month post-training intervals.
- Rescheduling status (`rescheduled`), explicit `next_contact_date`, and qualitative `trainer_notes`.
- Computed `is_overdue` and `is_due_today` serializer flags rendered with dynamic badge indicators.
- Strict consent gate: If participant consent is withdrawn, outreach dispatch is automatically blocked.

### Audit Logging & Compliant CSV Reports
- **UTF-8 BOM Prepending**: CSV exports (`\ufeff`) ensure flawless rendering of Devanagari, Tamil, Bengali, and all Indian scripts in Microsoft Excel.
- **Consent Masking**: Participants who have withdrawn consent have their names and contact details masked in compliance with data minimization standards.
- **Download Audit Trail**: Report downloads generate immutable records in `AuditLog`, inspectable via `/api/reports/history/`.

---

## 3. 11-Language Localization
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

## 4. Local Setup & Execution Guide

### Prerequisites
- Python 3.12+ (or 3.14)
- Git / PowerShell / Terminal

### Step 1: Install Python Dependencies
```bash
cd d:\vs
pip install -r requirements.txt
```

### Step 2: Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
copy .env.example .env
```
Default `.env` settings are already configured for SQLite local fallback and console email backend (OTPs display directly in the terminal).

### Step 3: Run Database Migrations
```bash
python manage.py migrate
```

### Step 4: Seed Demo Records (Idempotent)
Populates initial demo trainers, trainees, placements, consents, courses, enrollments, certificates, outcomes, and notifications:
```bash
python manage.py seed_demo_data
```

### Step 5: Start the Development Server
```bash
python manage.py runserver 127.0.0.1:8000
```
Open your browser at [http://127.0.0.1:8000/login/](http://127.0.0.1:8000/login/).

---

## 5. Default Demo Credentials

All demo accounts share the password: `Atlas@2026!`

| Role | Email | Field Atlas ID | Initial Landing View |
| :--- | :--- | :--- | :--- |
| **Trainer** | `trainer@fieldatlas.in` | `FA-TR-1001` | `/trainer/` (Trainer Dashboard) |
| **Trainee** | `trainee@fieldatlas.in` | `FA-24-0182` | `/trainee/` (Learner Portal) |
| **Admin** | `admin@fieldatlas.in` | `FA-AD-0001` | `/admin/` & `/trainer/` |

---

## 6. Docker Deployment Guide

To launch the full production-ready stack with Django and MySQL:

```bash
docker-compose up -d --build
```
This automatically initializes:
- A MySQL 8.0 container on port 3306 with health check verification.
- A Django web application container running on port 8000 with PyMySQL.

---

## 7. Database Backup Command

To create an instant snapshot of the application state:
```bash
python manage.py backup_database
```
Backups are saved to `backups/field_atlas_backup_<timestamp>.json`.

---

## 8. Complete REST API Contract

All REST JSON endpoints are prefixed with `/api/` (except `/health/` and public verification pages):

### System & Health
- `GET /health/` — Platform and database connectivity health probe.
- `GET /certificate/verify/<token>/` — Public credential verification HTML page.

### Authentication & Profiles
- `POST /api/auth/register/` — Register with mandatory OTP validation.
- `POST /api/auth/login/` — Authenticate with 5-attempt temporary lockout.
- `POST /api/auth/logout/` — End session.
- `POST /api/auth/send-otp/` — Request 6-digit email OTP (rate-limited).
- `POST /api/auth/verify-otp/` — Verify OTP (HMAC constant-time check).
- `POST /api/auth/password-reset/` — Reset password with OTP.
- `POST /api/auth/change-password/` — Change password for logged-in user.
- `GET /api/auth/me/` — Return current session user details and role.
- `GET /api/profile/` & `PATCH /api/profile/` — Profile retrieval and update.
- `POST /api/profile/photo/` — Profile photo upload (Pillow validation, max 2MB).
- `GET /api/i18n/languages/` — List all 11 supported languages.
- `POST /api/i18n/set-language/` — Set user language preference.

### Course Management (Trainer Scoped)
- `GET /api/courses/` & `POST /api/courses/` — List trainer courses or create a new course.
- `GET /api/courses/<id>/` & `PATCH /api/courses/<id>/` — Retrieve or update course details.
- `POST /api/courses/<id>/publish/` — Publish course to make it visible to trainees.
- `POST /api/courses/<id>/close/` — Close course applications.
- `GET /api/courses/<id>/applications/` — View applications submitted for a course.
- `POST /api/courses/applications/<id>/review/` — Approve or reject an application.
- `GET /api/courses/<id>/enrollments/` — Roster of enrolled learners with progress.
- `PATCH /api/courses/enrollments/<id>/` — Update learner progress percentage and completion notes.
- `POST /api/courses/enrollments/<id>/certificate/` — Issue verifiable ReportLab PDF certificate.
- `POST /api/courses/enrollments/<id>/remind/` — Dispatch outcome survey reminder.
- `POST /api/courses/outcomes/<id>/verify/` — Mark reported employment outcome as verified.
- `GET /api/courses/<id>/analytics/` — Comprehensive outcomes analytics breakdown.
- `GET /api/courses/<id>/performance/` — Transparent course performance metrics with k-anonymity privacy safeguards.

### Trainee Self-Service & Learning
- `GET /api/trainee/me/dashboard/` — Personal timeline, placement, and check-in prompt.
- `GET /api/trainee/courses/` — Browse published courses with search and category filtering.
- `POST /api/trainee/courses/<id>/apply/` — Apply for a course with motivation statement.
- `GET /api/trainee/me/applications/` — View submitted course applications.
- `GET /api/trainee/me/enrollments/` — View enrolled courses, progress, and certificate download links.
- `GET /api/trainee/me/enrollments/<id>/outcome/` — Retrieve recorded employment outcome.
- `POST /api/trainee/me/enrollments/<id>/outcome/` — Submit or update employment outcome survey.
- `POST /api/trainee/me/follow-ups/<id>/respond/` — Submit check-in response.
- `GET /api/trainee/me/progress-report/` — Structured learner progress summary document.
- `POST /api/trainee/me/consent/` — Manage personal consent status.

### Certificates & Notifications
- `GET /api/certificates/<id>/download/` — Download certificate PDF file.
- `GET /api/certificates/verify/<token>/` — Public API to verify certificate authenticity.
- `GET /api/notifications/` — List user notifications with unread count.
- `POST /api/notifications/<id>/read/` — Mark specific notification as read.
- `POST /api/notifications/read-all/` — Mark all notifications as read.

### Longitudinal Follow-ups & Reports
- `GET /api/trainer/dashboard/` — Dynamic SQL-driven KPI metrics and charts.
- `GET /api/outcomes/trainees/` — Query scoped trainees with pagination and filters.
- `POST /api/outcomes/trainees/` — Create trainee with atomic intake consent.
- `GET /api/outcomes/follow-ups/` — List scoped follow-up queue with overdue flags.
- `PATCH /api/outcomes/follow-ups/<id>/` — Reschedule follow-up and add trainer notes.
- `POST /api/outcomes/follow-ups/<id>/send/` — Dispatch outreach attempt.
- `GET /api/outcomes/placements/` — List scoped placements.
- `POST /api/outcomes/consents/` — Grant or withdraw consent.
- `GET /api/reports/provider-export/` — Download provider performance CSV (UTF-8 BOM).
- `GET /api/reports/impact-export/` — Download consent-masked impact CSV (UTF-8 BOM).
- `GET /api/reports/history/` — Audit history of report exports.

---

## 9. Automated Test Suite

Run the full automated test suite:
```bash
python manage.py test outcomes
```

### Verification Output
```
Ran 28 tests in 31.670s

OK
```
Covering:
- Course creation, update, publication, and closure lifecycle
- Trainee course application submission, trainer review, approval, and enrollment creation
- Strict object-level trainer isolation (HTTP 403 on foreign course review, progress update, and certificate issuance)
- Trainee progress tracking, ReportLab landscape PDF certificate generation, and secure download
- Public certificate verification via both API and dedicated HTML verification landing page
- Trainee post-skilling outcome submission and trainer verification
- k-anonymity privacy safeguards hiding average wage when responses are under 5
- In-app notification delivery, unread counter, and mark-as-read endpoints
- Trainer data isolation (HTTP 403 on foreign trainee view, update, outreach, reschedule, and exports)
- Unrestricted Admin access & Trainee self-service isolation
- Cryptographic HMAC OTP generation, single-use invalidation, and expiration
- 5-attempt account lockout rate-limiting and anti-enumeration
- Weak password rejection via Django password validators
- Pillow profile photo upload sanitization (valid image passes, fake/oversized files rejected, old file cleanup)
- Follow-up rescheduling workflow with `next_contact_date`, `trainer_notes`, and overdue/due-today flags
- Provider name canonicalization across naming variations
- Scoped CSV exports with UTF-8 BOM encoding and consent masking
- Platform health check probe (`/health/`) returning HTTP 200
