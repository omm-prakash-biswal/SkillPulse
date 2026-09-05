"""
WSGI config for Field Atlas project.
It exposes the WSGI callable as a module-level variable named `application`.
For Vercel serverless deployment, `app = application` is exposed.
"""
import os
import shutil
from pathlib import Path
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

# In Vercel serverless environment, copy db.sqlite3 to /tmp if it does not already exist
if os.getenv('VERCEL') and os.getenv('USE_MYSQL', 'False').lower() not in ('true', '1', 'yes'):
    tmp_db = Path('/tmp/db.sqlite3')
    base_db = Path(__file__).resolve().parent.parent / 'db.sqlite3'
    if not tmp_db.exists() and base_db.exists():
        try:
            shutil.copyfile(base_db, tmp_db)
        except Exception:
            pass

application = get_wsgi_application()
app = application
