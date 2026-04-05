"""
SQLAlchemy models for the macro dashboard.

Usage (after you create the Flask app):
    from models import db
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///macro.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    with app.app_context():
        db.create_all()
"""

from __future__ import annotations
from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Index, UniqueConstraint

# Flask-SQLAlchemy extension (bound to the app via db.init_app in app factory)
db = SQLAlchemy()


###  Tables for Economic Data ###
# Reference data: economies you plot (ISO 3166-1 alpha-3 is stable for APIs)
class Country(db.Model):
    __tablename__ = "countries"

    id = db.Column(db.Integer, primary_key=True)
    iso3 = db.Column(db.String(3), unique=True, nullable=False, index=True)
    name = db.Column(db.String(255), nullable=False)

    def __repr__(self) -> str:
        return f"<Country {self.iso3}>"


# Reference data: indicators (GDP per capita, CPI, TFP, …)
class Metric(db.Model):
    __tablename__ = "metrics"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(64), unique=True, nullable=False, index=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    unit = db.Column(db.String(128))
    frequency = db.Column(db.String(16))  # e.g. annual, quarterly

    def __repr__(self) -> str:
        return f"<Metric {self.code}>"


# Time series: one row = one (country, metric, period) value
class Observation(db.Model):
    __tablename__ = "observations"

    id = db.Column(db.Integer, primary_key=True)

    # Foreign keys: which country and which metric this point belongs to
    country_id = db.Column(db.Integer, db.ForeignKey("countries.id"), nullable=False)
    metric_id = db.Column(db.Integer, db.ForeignKey("metrics.id"), nullable=False)

    # Time identifier as text so annual ("2020") and quarterly ("2020-Q1") share one column
    period = db.Column(db.String(32), nullable=False)

    # Measured value and when this row was written (useful for refresh / auditing)
    value = db.Column(db.Float, nullable=False)
    ingested_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
    )

    # ORM navigation: country.observations / metric.observations (object-oriented mapping)
    country = db.relationship("Country", backref=db.backref("observations", lazy="dynamic"))
    metric = db.relationship("Metric", backref=db.backref("observations", lazy="dynamic"))

    # Table rules: no duplicate points; index shaped for typical series queries
    __table_args__ = (
        UniqueConstraint(
            "country_id",
            "metric_id",
            "period",
            name="uq_obs_country_metric_period",
        ),
        Index("ix_obs_metric_country_period", "metric_id", "country_id", "period"),
    )

    def __repr__(self) -> str:
        return f"<Observation c={self.country_id} m={self.metric_id} {self.period}>"


### Tables for User Data ###
class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(512), nullable=False)
    registered_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    last_login = db.Column(db.DateTime, nullable=True)

    preferences = db.relationship(
        "UserPreferences",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<User {self.username}>"


### Tables for User Preferences ###
class UserPreferences(db.Model):
    __tablename__ = "user_preferences"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        unique=True,
    )
    # Dashboard layout, theme, default selections, etc.
    preferences = db.Column(db.JSON, nullable=False, default=lambda: {})

    user = db.relationship("User", back_populates="preferences")

    def __repr__(self) -> str:
        return f"<UserPreferences {self.user_id}>"

