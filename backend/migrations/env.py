from __future__ import with_statement

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from alembic import context
from sqlalchemy import engine_from_config, pool
from flask import current_app

# App factory and metadata
def get_app():
    from app import create_app
    return create_app(os.environ.get("FLASK_ENV") or "default")

app = get_app()
with app.app_context():
    config = context.config
    config.set_main_option("sqlalchemy.url", current_app.config["SQLALCHEMY_DATABASE_URI"])
    from app import db
    from app.models import User, Meal, Workout  # noqa: F401
    target_metadata = db.metadata

    def run_migrations_offline():
        url = config.get_main_option("sqlalchemy.url")
        context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
        with context.begin_transaction():
            context.run_migrations()

    def run_migrations_online():
        section = config.get_section(config.config_ini_section) or {}
        section["sqlalchemy.url"] = current_app.config["SQLALCHEMY_DATABASE_URI"]
        connectable = engine_from_config(
            section,
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
        )
        with connectable.connect() as connection:
            context.configure(connection=connection, target_metadata=target_metadata)
            with context.begin_transaction():
                context.run_migrations()

    if context.is_offline_mode():
        run_migrations_offline()
    else:
        run_migrations_online()
