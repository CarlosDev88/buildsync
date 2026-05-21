# BuildSync
 
> ERP + CRM backend for real-estate construction companies — from the public
> property showcase all the way to on-site cost control.
 
BuildSync is a modular Django backend that models the full lifecycle of a real
estate developer: publishing projects and units to a public catalog, capturing
and qualifying leads, managing the mortgage/credit pipeline, and tracking
construction work on the ground (phases, a task Kanban, and real-vs-planned
material consumption).
 
It is built as a set of focused, decoupled Django apps that communicate through
clear domain boundaries, exposing both a **REST API** (Django REST Framework +
JWT) and a **GraphQL API** (Strawberry) for the public showcase.
 
---
 
## Table of contents
 
- [Architecture](#architecture)
- [Modules](#modules)
- [Tech stack](#tech-stack)
- [APIs](#apis)
- [Getting started](#getting-started)
- [Authentication](#authentication)
- [Project structure](#project-structure)
- [Roadmap](#roadmap)
---
 
## Architecture
 
The system is split into independent Django apps, each owning one domain. The
`catalogue` app is the single source of truth for projects and units; the other
modules reference it rather than duplicating data.
 
```
        ┌────────────┐
        │  catalogue │  Projects & units (public showcase, GraphQL)
        └─────┬──────┘
              │ referenced by
   ┌──────────┼───────────────┬───────────────┐
   ▼          ▼               ▼               ▼
┌──────┐  ┌──────────────┐  ┌─────┐      ┌──────────┐
│ crm  │  │ construction │  │loan │      │  users   │
│leads │  │ phases/kanban│  │flow │      │ JWT auth │
└──────┘  └──────────────┘  └─────┘      └──────────┘
```
 
Two design decisions worth highlighting:
 
- **EAV for unit features.** Properties store their characteristics (area,
  bedrooms, etc.) through a flexible entity-attribute-value model, so new
  feature types can be added without schema migrations.
- **APU-based cost control.** Construction activities are defined as "recipes"
  (Análisis de Precios Unitarios) of resources; tasks then record what was
  *actually* consumed, making the planned-vs-real gap measurable.
---
 
## Modules
 
### `catalogue` — Public showcase
The customer-facing side. Exposes projects and their units (apartments, houses,
commercial, lots) through a **public GraphQL endpoint** (no auth required).
Supports rich filtering by status, type, price range, area and bedrooms, with
queries optimized via `select_related` / `prefetch_related` to avoid N+1.
 
### `construction` — On-site ERP
The operational core for building work:
- **Project phases** (foundation, structure, finishes…) with status tracking.
- **Task Kanban** (`TODO → IN_PROGRESS → REVIEW → DONE`), each task tied to a
  unit and to an activity (APU).
- **Resources** (materials, labor, equipment) with construction-standard units
  (kg, m³, m², bag, hour…).
- **Consumption reports** that log real resource usage against each task,
  surfacing the planned-vs-actual cost difference.
### `crm` — Sales pipeline
Lead and opportunity management for the sales room:
- **Clients** with lead source tracking (Facebook, walk-in, referral, website).
- **Financial profiles** (income, savings, debt flags) for credit pre-qual.
- **Opportunities**, **documents** (stored in **AWS S3** via keys, with
  presigned URLs generated per request), and an **interaction log**
  (calls, WhatsApp, meetings, system notes).
### `loanflow` — Credit pipeline
Mortgage / credit application flow connecting qualified opportunities to
financing.
 
### `users` — Identity
Custom user model (`users.CustomUser`) with **JWT authentication**. The token
payload carries the user's role to avoid an extra DB round-trip per request.
 
---
 
## Tech stack
 
| Layer            | Technology |
| ---------------- | ---------- |
| Language         | Python |
| Framework        | Django 6 |
| REST API         | Django REST Framework |
| Auth             | DRF SimpleJWT (Bearer tokens) |
| GraphQL          | Strawberry |
| Database         | SQLite (development) |
| File storage     | AWS S3 (documents) |
 
---
 
## APIs
 
BuildSync exposes two complementary APIs:
 
- **REST (DRF):** authenticated by default (JWT), with page-number pagination
  (`PAGE_SIZE = 20`). Internal/operational endpoints (CRM, construction, etc.).
- **GraphQL (Strawberry):** the `catalogue` showcase. Public read access for
  visitors browsing projects and units.
Example GraphQL queries available in the showcase schema:
 
| Query        | Description |
| ------------ | ----------- |
| `projects`   | Project cards, optionally filtered by status / availability |
| `project`    | Full project detail with all units and points of interest |
| `properties` | Filterable unit catalog (status, type, price, area, bedrooms) |
| `property`   | Single unit with all its features |
 
---
 
## Getting started
 
### Requirements
- Python 3.12+
- pip / virtualenv
### Setup
 
```bash
# 1. Clone
git clone https://github.com/CarlosDev88/buildsync.git
cd buildsync
 
# 2. Virtual environment
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
 
# 3. Install dependencies
pip install django djangorestframework djangorestframework-simplejwt strawberry-graphql
# (or: pip install -r requirements.txt once you add one)
 
# 4. Migrations
python manage.py migrate
 
# 5. Admin user
python manage.py createsuperuser
 
# 6. Run
python manage.py runserver
```
 
The server runs at `http://127.0.0.1:8000/` and the Django admin at
`http://127.0.0.1:8000/admin/`.
 
> **Note:** the repo currently ships with development settings (`DEBUG = True`,
> SQLite, an inline `SECRET_KEY`). Before any real deployment, move secrets to
> environment variables, switch to PostgreSQL, set `DEBUG = False` and configure
> `ALLOWED_HOSTS`. See [Roadmap](#roadmap).
 
---
 
## Authentication
 
The API uses JWT (DRF SimpleJWT):
 
- **Access token:** 8 hours (a work day)
- **Refresh token:** 7 days, rotated on use
- **Header:** `Authorization: Bearer <access_token>`
Public endpoints (showcase / simulator) override the default permission with
`AllowAny`.
 
---
 
## Project structure
 
```
buildsync/
├── core/            # Settings, root URLs, GraphQL schema (RootQuery)
├── users/           # Custom user model + JWT serializers
├── catalogue/       # Projects, units, features (EAV) + GraphQL showcase
├── construction/    # Phases, Kanban tasks, resources, APUs, consumption
├── crm/             # Clients, financial profiles, opportunities, documents
├── loanflow/        # Credit / mortgage flow
├── manage.py
└── db.sqlite3
```
 
---
 
## Roadmap
 
Things intended for production hardening and future modules:
 
- [ ] Move `SECRET_KEY` and config to environment variables
- [ ] Switch from SQLite to PostgreSQL
- [ ] Add `requirements.txt` / dependency lockfile
- [ ] Enable JWT blacklist after rotation in production
- [ ] Extend the GraphQL schema to CRM and LoanFlow modules
- [ ] Containerize (Docker) and add CI
---
 
## Author
 
**Carlos Rueda** — Frontend Developer
[LinkedIn](https://www.linkedin.com/in/carlos-rueda-calier)
