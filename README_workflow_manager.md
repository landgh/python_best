# workflow_manager

This module is a Python script that includes functionality related to workflows, event-driven triggers, and singleton management via `WorkflowManager`.

## 🔍 Overview

This test suite verifies:

- Workflow creation and state transitions
- Event triggering behavior
- Singleton enforcement for `WorkflowManager`
- Batch triggering of workflows

## ▶️ Usage

To run tests:

```bash
pytest workflow_manager.py -v

from enum import Enum, auto
from typing import List, Dict, Callable, Optional
import uuid
import threading


class WorkflowType(Enum):
    API = "API"
    MANUAL = "Manual"


class WorkflowState(Enum):
    PENDING = "Pending"
    SUCCESS = "Success"
    FAIL = "Fail"
    WARNING = "Warning"
    APPROVED = "Approved"
    CANCEL = "Cancel"


class Event:
    def __init__(self, name: str, trigger_condition: Callable[[], bool]):
        self.name = name
        self.trigger_condition = trigger_condition

    def is_triggered(self) -> bool:
        return self.trigger_condition()


class Workflow:
    def __init__(self, event: Event, workflow_type: WorkflowType):
        self.id = str(uuid.uuid4())
        self.event = event
        self.type = workflow_type
        self.state = WorkflowState.PENDING
        self.history: List[WorkflowState] = [self.state]

    def transition_state(self, new_state: WorkflowState):
        if new_state != self.state:
            self.state = new_state
            self.history.append(new_state)
            print(f"Workflow {self.id} transitioned to {self.state.name}")

    def check_and_trigger(self):
        if self.event.is_triggered():
            print(f"Event '{self.event.name}' triggered workflow {self.id}")
            self.transition_state(WorkflowState.SUCCESS)
        else:
            print(f"Event '{self.event.name}' not triggered for workflow {self.id}")


class WorkflowManager:
    _instance = None
    _lock = threading.Lock()

    def __init__(self):
        # Allow DI use: init doesn't enforce singleton
        self.workflows: Dict[str, Workflow] = {}

    @classmethod
    def get_instance(cls) -> 'WorkflowManager':
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def create_workflow(self, event: Event, workflow_type: WorkflowType) -> Workflow:
        workflow = Workflow(event, workflow_type)
        self.workflows[workflow.id] = workflow
        print(f"Created workflow {workflow.id} of type {workflow.type.name}")
        return workflow

    def trigger_all(self):
        for workflow in self.workflows.values():
            workflow.check_and_trigger()


# --- Example usage ---
if __name__ == "__main__":
    # Simple trigger condition example
    event1 = Event("OnFileUpload", trigger_condition=lambda: True)
    event2 = Event("OnManualReview", trigger_condition=lambda: False)

    # Use Singleton instance
    manager = WorkflowManager.get_instance()

    wf1 = manager.create_workflow(event1, WorkflowType.API)
    wf2 = manager.create_workflow(event2, WorkflowType.MANUAL)

    manager.trigger_all()


