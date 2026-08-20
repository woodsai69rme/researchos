"""
ResearchOS Database Schema & SQLAlchemy Persistence Layer
Supports SQLite (zero-install) and PostgreSQL
"""
import json
from datetime import datetime
from typing import Any, Dict, List
from sqlalchemy import (
    Column, String, Text, Float, Boolean, Integer, DateTime, JSON, ForeignKey, create_engine
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from researchos.packages.core.config import settings

Base = declarative_base()


class ResearchRunRecord(Base):
    __tablename__ = "research_runs"

    id = Column(String(64), primary_key=True)
    query = Column(Text, nullable=False)
    operating_mode = Column(String(32), default="FREE_ONLY")
    depth = Column(String(32), default="normal")
    location = Column(String(128), default="Australia")
    actual_spend_aud = Column(Float, default=0.0)
    report_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class WatchlistRecord(Base):
    __tablename__ = "watchlists"

    id = Column(String(64), primary_key=True)
    title = Column(String(256), nullable=False)
    query = Column(Text, nullable=False)
    category = Column(String(64), default="general")
    interval_hours = Column(Integer, default=12)
    last_checked = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class AlertRecord(Base):
    __tablename__ = "alerts"

    id = Column(String(64), primary_key=True)
    watchlist_id = Column(String(64), nullable=True)
    title = Column(String(256), nullable=False)
    message = Column(Text, nullable=False)
    significance = Column(String(32), default="MEDIUM")
    created_at = Column(DateTime, default=datetime.utcnow)


import os
from pathlib import Path

# Ensure local SQLite data directory exists
data_dir = Path(__file__).resolve().parent.parent / "data"
os.makedirs(data_dir, exist_ok=True)

clean_db_url = settings.DATABASE_URL.replace("+aiosqlite", "").replace("+asyncpg", "")
if clean_db_url.startswith("sqlite"):
    if "///" in clean_db_url and not clean_db_url.startswith("sqlite:////"):
        # Make absolute path to data dir
        clean_db_url = f"sqlite:///{str(data_dir / 'researchos.db').replace('\\', '/')}"
    engine = create_engine(clean_db_url, connect_args={"check_same_thread": False}, echo=False)
else:
    engine = create_engine(clean_db_url, echo=False)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    Base.metadata.create_all(bind=engine)
