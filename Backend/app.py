"""
Flask application for the macro dashboard API.

Run from this folder (Backend):
    pip install -r requirements.txt
    flask --app app run --debug

Optional env:
    SECRET_KEY          — session/signing (set in production)
    DATABASE_URL        — overrides default SQLite in instance/macro.db
"""

# Load packages
from __future__ import annotations
import os
from pathlib import Path
from flask import Flask, jsonify, request
from flask_cors import CORS   # Adds HTTP headers to allow the Vue dev server (or any origin) to call /api/*

# Load models.py
from models import Country, Metric, Observation, db

# Create the default SQLite URI
def _default_sqlite_uri() -> str:
    """SQLite file under Backend/instance/macro.db (created on first run)."""
    instance = Path(__file__).resolve().parent / "instance"
    instance.mkdir(parents=True, exist_ok=True)
    return "sqlite:///" + (instance / "macro.db").resolve().as_posix()

# Create the app
def create_app() -> Flask:
    """Application factory: config, database, CORS, routes."""
    app = Flask(__name__)

    # Core Flask settings
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-change-me")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        os.environ.get("DATABASE_URL") or _default_sqlite_uri()
    )

    # Bind SQLAlchemy and allow the Vue dev server (or any origin) to call /api/*
    db.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Create tables if they do not exist (replace with Alembic migrations when you evolve schema)
    with app.app_context():
        db.create_all()

    register_routes(app)
    return app


def register_routes(app: Flask) -> None:
    """Attach all HTTP routes to the app (kept in one place for a small API)."""

    # Simple uptime check for deploys and frontend connection tests
    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok"})

    # Dropdown / picker data: all countries from the reference table
    @app.get("/api/countries")
    def list_countries():
        rows = Country.query.order_by(Country.name).all()
        return jsonify(
            [
                {"id": c.id, "iso3": c.iso3, "name": c.name}
                for c in rows
            ]
        )

    # Dropdown / picker data: all metrics (codes are what /api/series expects)
    @app.get("/api/metrics")
    def list_metrics():
        rows = Metric.query.order_by(Metric.name).all()
        return jsonify(
            [
                {
                    "id": m.id,
                    "code": m.code,
                    "name": m.name,
                    "description": m.description,
                    "unit": m.unit,
                    "frequency": m.frequency,
                }
                for m in rows
            ]
        )

    # Time series for charts: filter observations by country ISO3 + metric code (+ optional period range)
    @app.get("/api/series")
    def series():
        """
        Query params (repeat or comma-separated):
          country — ISO3 codes, e.g. country=USA&country=GBR or country=USA,GBR
          metric  — metric codes, e.g. metric=gdp_pc
          period_from, period_to — optional inclusive string bounds (lexicographic works for YYYY and YYYY-Qn)
        """
        countries = _parse_list_arg("country")
        metrics = _parse_list_arg("metric")
        if not countries or not metrics:
            return (
                jsonify(
                    {
                        "error": "Provide at least one `country` (ISO3) and one `metric` (code).",
                    }
                ),
                400,
            )

        period_from = request.args.get("period_from")
        period_to = request.args.get("period_to")

        q = (
            db.session.query(Observation, Country, Metric)
            .join(Country, Observation.country_id == Country.id)
            .join(Metric, Observation.metric_id == Metric.id)
            .filter(Country.iso3.in_(countries))
            .filter(Metric.code.in_(metrics))
        )
        if period_from:
            q = q.filter(Observation.period >= period_from)
        if period_to:
            q = q.filter(Observation.period <= period_to)

        rows = q.order_by(
            Metric.code,
            Country.iso3,
            Observation.period,
        ).all()

        # One array per (country, metric) for easy chart binding on the frontend
        grouped: dict[tuple[str, str], list[dict]] = {}
        for obs, country, metric in rows:
            key = (country.iso3, metric.code)
            grouped.setdefault(key, []).append(
                {"period": obs.period, "value": obs.value}
            )

        out = []
        for (iso3, code), points in grouped.items():
            out.append(
                {
                    "country_iso3": iso3,
                    "metric_code": code,
                    "points": points,
                }
            )

        return jsonify({"series": out})


def _parse_list_arg(name: str) -> list[str]:
    """Normalize query lists: ?country=A&country=B and ?country=A,B both work."""
    raw = request.args.getlist(name)
    if not raw:
        single = request.args.get(name)
        if single:
            raw = [single]
    parts: list[str] = []
    for chunk in raw:
        parts.extend(p.strip() for p in chunk.split(",") if p.strip())
    return parts


# WSGI entry: `flask --app app run` imports this module and uses `app`
app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
