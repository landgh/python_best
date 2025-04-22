import pytest
from unittest.mock import Mock
from src.process_flow.workflow_manager import WorkflowManager, Event, WorkflowType, WorkflowState


@pytest.fixture(autouse=True)
def reset_singleton():
    WorkflowManager._instance = None
    yield


def test_create_workflow():
    manager = WorkflowManager()
    event = Event("TestEvent", trigger_condition=lambda: True)
    workflow = manager.create_workflow(event, WorkflowType.API)

    # Add a breakpoint for debugging
    # pytest.set_trace()

    assert workflow.event.name == "TestEvent"
    assert workflow.type == WorkflowType.API
    assert workflow.state == WorkflowState.PENDING
    assert workflow.id in manager.workflows


def test_workflow_triggered_successfully():
    manager = WorkflowManager()
    event = Event("AutoTrigger", trigger_condition=lambda: True)
    workflow = manager.create_workflow(event, WorkflowType.API)

    workflow.check_and_trigger()
    assert workflow.state == WorkflowState.SUCCESS
    assert WorkflowState.SUCCESS in workflow.history


def test_workflow_not_triggered():
    manager = WorkflowManager()
    event = Event("NoTrigger", trigger_condition=lambda: False)
    workflow = manager.create_workflow(event, WorkflowType.MANUAL)

    workflow.check_and_trigger()
    assert workflow.state == WorkflowState.PENDING
    assert WorkflowState.SUCCESS not in workflow.history


def test_singleton_instance():
    instance1 = WorkflowManager.get_instance()
    instance2 = WorkflowManager.get_instance()

    assert instance1 is instance2


def test_trigger_all():
    manager = WorkflowManager()
    event_true = Event("Trigger1", trigger_condition=lambda: True)
    event_false = Event("Trigger2", trigger_condition=lambda: False)

    wf1 = manager.create_workflow(event_true, WorkflowType.API)
    wf2 = manager.create_workflow(event_false, WorkflowType.MANUAL)

    manager.trigger_all()

    assert wf1.state == WorkflowState.SUCCESS
    assert wf2.state == WorkflowState.PENDING
