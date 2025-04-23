import sys
import os

from sqlalchemy import create_engine, Column, String, DateTime, ForeignKey, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from src.db.model.event import Event
from src.db.model.workflow import Workflow  # Use absolute imports
from src.db.model.base import Base  # Import shared Base
"""
Initialize the database with Event and Workflow tables.

to run this script, use the following command:
python -m src.db.init_db
or run it directly if you have the src directory in your PYTHONPATH:
# Example:
# PYTHONPATH=/d/mypython/python_best main $ python src/db/init_db.py
# or if you have the src directory in your PYTHONPATH:
# PYTHONPATH=
/d/mypython/python_best main $ python -m src.db.init_db
"""
def init_db():
    engine = create_engine('sqlite:///:memory:', echo=False)
    # Create both Event and Workflow tables
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()


if __name__ == "__main__":
    session = init_db()
    # Check if tables are created
    inspector = inspect(session.bind)  # Use inspect to get the inspector
    tables = inspector.get_table_names()
    print("Tables in the database:", tables)
    print("✅ Event and Workflow tables created in memory using SQLAlchemy.")