from enum import Enum, auto

class EventType(Enum):
    API = "API"
    MANUAL = "Manual"

class WorkflowType(Enum):
    FULL = "Full"
    CATEGORY = "Category"


class WorkflowState(Enum):
    RUNNING = "Running"
    SUCCESS = "Success"
    FAIL = "Fail"
    WARNING = "Warning"
    APPROVED = "Approved"
    CANCEL = "Cancel"