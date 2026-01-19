"""
Database module for CCMC Patient Allocator.
Provides SQLAlchemy ORM models and database utilities for PostgreSQL/SQLite.
"""

import os
from datetime import datetime
from contextlib import contextmanager
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, CheckConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Database URL handling for Railway (PostgreSQL) or local (SQLite)
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///patients.db')
# Railway uses postgres:// but SQLAlchemy requires postgresql://
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

# Create engine with connection pooling for multi-user support
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=300,    # Recycle connections every 5 minutes
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ============================================================================
# Database Models
# ============================================================================

class MasterPhysician(Base):
    """Master list of all known physicians."""
    __tablename__ = 'master_physicians'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    default_team = Column(String(1), default='A')
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        CheckConstraint("default_team IN ('A', 'B', 'N')", name='valid_default_team'),
    )


class Physician(Base):
    """Current working physicians with patient data."""
    __tablename__ = 'physicians'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    team = Column(String(1), nullable=False, default='A')
    is_new = Column(Boolean, default=False)
    is_buffer = Column(Boolean, default=False)
    is_working = Column(Boolean, default=True)
    total_patients = Column(Integer, default=0)
    step_down_patients = Column(Integer, default=0)
    transferred_patients = Column(Integer, default=0)
    traded_patients = Column(Integer, default=0)
    yesterday_name = Column(String(100), nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        CheckConstraint("team IN ('A', 'B', 'N')", name='valid_team'),
    )


class UserSelection(Base):
    """User's physician selections for building the working roster."""
    __tablename__ = 'user_selections'

    id = Column(Integer, primary_key=True, autoincrement=True)
    physician_name = Column(String(100), nullable=False)
    team_assignment = Column(String(1), default='A')
    is_selected = Column(Boolean, default=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        CheckConstraint("team_assignment IN ('A', 'B', 'N')", name='valid_selection_team'),
    )


class YesterdayPhysician(Base):
    """Yesterday's working physicians for reference."""
    __tablename__ = 'yesterday_physicians'

    id = Column(Integer, primary_key=True, autoincrement=True)
    physician_name = Column(String(100), nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Parameter(Base):
    """Allocation parameters configuration."""
    __tablename__ = 'parameters'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True, default='default')
    n_total_new_patients = Column(Integer, default=20)
    n_A_new_patients = Column(Integer, default=10)
    n_B_new_patients = Column(Integer, default=8)
    n_N_new_patients = Column(Integer, default=2)
    n_step_down_patients = Column(Integer, default=0)
    minimum_patients = Column(Integer, default=10)
    maximum_patients = Column(Integer, default=20)
    new_start_number = Column(Integer, default=5)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class DefaultPhysician(Base):
    """Default physician configuration for demo/reset."""
    __tablename__ = 'default_physicians'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    team = Column(String(1), default='A')
    is_new = Column(Boolean, default=False)
    is_buffer = Column(Boolean, default=False)
    is_working = Column(Boolean, default=True)
    total_patients = Column(Integer, default=0)
    step_down_patients = Column(Integer, default=0)
    traded_patients = Column(Integer, default=0)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        CheckConstraint("team IN ('A', 'B', 'N')", name='valid_default_phys_team'),
    )


class DataVersion(Base):
    """Version tracking for multi-user conflict detection."""
    __tablename__ = 'data_version'

    id = Column(Integer, primary_key=True, default=1)
    version = Column(Integer, default=1)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        CheckConstraint("id = 1", name='single_row'),
    )


# ============================================================================
# Database Utilities
# ============================================================================

@contextmanager
def get_db():
    """Context manager for database sessions with automatic commit/rollback."""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def init_database():
    """Create all tables if they don't exist."""
    Base.metadata.create_all(bind=engine)


def get_data_version():
    """Get current data version for conflict detection."""
    with get_db() as db:
        version_row = db.query(DataVersion).first()
        if version_row:
            return version_row.version
        return 0


def increment_data_version():
    """Increment data version after changes."""
    with get_db() as db:
        version_row = db.query(DataVersion).first()
        if version_row:
            version_row.version += 1
            version_row.updated_at = datetime.utcnow()
        else:
            db.add(DataVersion(id=1, version=1))
