from enum import Enum, auto

class WorkflowType(Enum):
    API = "API"
    MANUAL = "Manual"


class WorkflowState(Enum):
    RUNNING = "Running"
    SUCCESS = "Success"
    FAIL = "Fail"
    WARNING = "Warning"
    APPROVED = "Approved"
    CANCEL = "Cancel"