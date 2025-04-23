import sys
import os

from sqlalchemy import create_engine, Column, String, DateTime, ForeignKey, inspect
from datetime import datetime, timezone
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from src.db.db_enum import EventType, WorkflowState, WorkflowType
from src.db.model.event import Event
from src.db.model.workflow import Workflow  # Use absolute imports
from src.db.model.base import Base  # Import shared Base

""" 
Initialize the database with Event and Workflow tables and populate them with sample data.
To run this script, use the following command:
    python -m src.db.init_db
or run it directly if you have the src directory in your PYTHONPATH:
Example:
    PYTHONPATH=/d/mypython/python_best main $ python src/db/init_db.py
    or if you have the src directory in your PYTHONPATH:
    PYTHONPATH=/d/mypython/python_best main $ python -m src.db.init_db
 """
def populate_data(session):
    # Create sample data for Event and Workflow tables
    event1 = Event(data_source="MF", event_type=EventType.API.value)
    event2 = Event(data_source="SF", event_type=EventType.MANUAL.value)

    # Add data to the session
    session.add_all([event1, event2])
    
    # need to commit first to see event1.id
    session.commit()

    print(f"event1.id {event1.id}")
    workflow1 = Workflow(event_id=event1.id, workflow_type=WorkflowType.FULL.value, workflow_state=WorkflowState.RUNNING.value)
    workflow2 = Workflow(event_id=event2.id, workflow_type=WorkflowType.CATEGORY.value, workflow_state=WorkflowState.RUNNING.value)
    session.add_all([workflow1, workflow2])
    session.commit()
    
    print("✅ Sample data added to Event and Workflow tables.")

def init_db():
    engine = create_engine('sqlite:///:memory:', echo=False)
    # Create both Event and Workflow tables
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()

def fetch_data(session):
    # Query the Event table
    events = session.query(Event).all()
    for e in events:
        print(f"Event ID: {e.id}, Data Source: {e.data_source}, Event Type: {e.event_type}, created_at: {e.created_at}")

    # Query the Workflow table (if needed)
    workflows = session.query(Workflow).all()
    for w in workflows:
        print(f"w is {w}")
        print(f"Workflow ID: {w.id}, workflow_type: {w.workflow_type}, workflow_state: {w.workflow_state}, created_at: {w.created_at}, Event ID: {w.event_id}")

if __name__ == "__main__":
    session = init_db()
    # Check if tables are created
    inspector = inspect(session.bind)  # Use inspect to get the inspector
    tables = inspector.get_table_names()
    print("Tables in the database:", tables)
    print("✅ Event and Workflow tables created in memory using SQLAlchemy.")

    # Populate sample data
    populate_data(session)

    # Fetch and print data from the Event table
    fetch_data(session)
    
    session.close()
    print("✅ Database initialization complete.")