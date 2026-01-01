# 🛒 Online Shop — Django Web App (Dockerized)

A **Django** web application for an online shop with a modular app structure, server‑rendered pages (**templates/**), and static assets (**static/**). The project includes **Docker / Docker Compose** for a reproducible development setup. citeturn1view0

---

## ✨ Highlights

- Modular Django apps: **users/** and **store/** citeturn1view0  
- Server‑rendered UI with **templates/** and **static/** directories citeturn1view0  
- Containerized workflow using **Dockerfile** + **docker-compose.yml** citeturn1view0  
- Frontend stack indicated by repo language stats: **HTML, CSS/SCSS, JavaScript** alongside **Python** citeturn1view0  

---

## 🧱 Tech Stack

- **Backend:** Django (Python) citeturn1view0  
- **Frontend:** Django Templates + static assets (HTML/CSS/SCSS/JS) citeturn1view0  
- **Containers:** Docker + Docker Compose citeturn1view0  

---

## 📁 Project Structure

```text
.
├── config/                # Django settings / urls / wsgi/asgi (project config)
├── store/                 # Shop domain app (catalog, etc.)
├── users/                 # User management/auth related app
├── templates/             # Server-rendered HTML templates
├── static/                # Static files (css/js/images)
├── manage.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

(Confirmed from repository root listing.) citeturn1view0

---

## ✅ Requirements

### Recommended
- **Docker** + **Docker Compose** (fastest onboarding)

### Alternative (Local)
- Python **3.10+** (recommended)
- A DB matching your settings (often Postgres in Docker setups)

---

## 🚀 Quick Start (Docker Compose)

```bash
# 1) Clone
git clone https://github.com/pouriashiralipour/online-shop.git
cd online-shop

# 2) Build & start containers
docker compose up --build
```

In a second terminal:

```bash
# 3) Run migrations
docker compose exec web python manage.py migrate

# 4) Create an admin user
docker compose exec web python manage.py createsuperuser

# 5) Collect static files (optional for prod-like runs)
docker compose exec web python manage.py collectstatic --noinput
```

Now open:
- `http://localhost:8000`

---

## 🧪 Running Locally (without Docker)

```bash
# 1) Virtualenv
python -m venv .venv
source .venv/bin/activate          # macOS/Linux
# .venv\Scripts\activate         # Windows

# 2) Dependencies
pip install -U pip
pip install -r requirements.txt

# 3) Migrations
python manage.py migrate

# 4) Run
python manage.py runserver
```

---

## ⚙️ Configuration (Environment Variables)

Create a `.env` file (recommended) and keep it **untracked**.

Suggested baseline (edit to match your settings):

```env
DJANGO_SETTINGS_MODULE=config.settings
SECRET_KEY=change-me
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

# If your project uses a database service (common in docker-compose):
DB_NAME=online_shop
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432

# Optional
CSRF_TRUSTED_ORIGINS=http://localhost:8000
```

If you don’t have env loading in settings yet, recommended options:
- `django-environ`
- `python-dotenv`

---

## 🔑 Authentication / Users app

The repository contains a dedicated `users/` app, which is typically used for:
- Custom user model or user profile
- Auth flows (login/signup)
- Account management

(Directory confirmed; implementation details may differ.) citeturn1view0

---

## 🏪 Store app

The repository contains a dedicated `store/` app, typically used for:
- Product/catalog pages
- Inventory / categories
- Cart / checkout / orders (if implemented)

(Directory confirmed; feature coverage depends on your implementation.) citeturn1view0

---

## 🧾 Templates & Static

- `templates/` → server-rendered HTML pages
- `static/` → CSS/JS/images (and potentially SCSS build outputs)

(Directories confirmed.) citeturn1view0

---

## 🧪 Testing

If you have tests configured, run:

```bash
# Local
python manage.py test

# Or, with Docker
docker compose exec web python manage.py test
```

> If you use pytest, add:
- `pytest`
- `pytest-django`
…and a `pytest.ini` at root.

---

## 🧯 Troubleshooting

### Docker build succeeds but app errors at runtime
- Check logs:
  ```bash
  docker compose logs -f
  ```
- Ensure migrations were applied:
  ```bash
  docker compose exec web python manage.py migrate
  ```

### Static files not loading
- In dev, ensure `DEBUG=True`
- In prod-like runs:
  ```bash
  docker compose exec web python manage.py collectstatic --noinput
  ```

### Port already in use
- Update port mapping in `docker-compose.yml` (host side), or stop conflicting process.

---

## 🗺️ Roadmap (Optional upgrades)

- [ ] Add OpenAPI docs (DRF Spectacular) if you expose APIs
- [ ] CI with GitHub Actions (lint + test)
- [ ] Pre-commit hooks (ruff/black/isort)
- [ ] Production compose: Gunicorn + Nginx + proper static/media handling
- [ ] Add screenshots + demo GIFs

---

## 📄 License

Check the repository for license details (if you add a `LICENSE` file, link it here).

---

## 👤 Author

**Pouria Shirali**  
- GitHub: https://github.com/pouriashiralipour  
- LinkedIn: https://linkedin.com/in/pouriashiralipour  
- Instagram: https://instagram.com/pouria.shirali

---

## ⭐ Repo naming suggestions

- `django-online-shop`
- `online-shop-django`
- `ecommerce-django-templates`
- `django-shop-docker`
