import pytest
import pandas as pd
from src.rollup_to_parent import rollup

# src/test_rollup_to_parent.py

@pytest.fixture
def sample_data():
    data = {
        'hierarchy': ['1', '1.2', '1.2.3', '1.2.3.4', '1.2.3.5', '2', '2.1', '2.1.1'],
        'amount1': [0, 0, 0, 10, 20, 0, 0, 15],
        'amount2': [5, 0, 0, 2, 3, 0, 0, 4]
    }
    return pd.DataFrame(data)

def test_rollup(monkeypatch: pytest.MonkeyPatch, sample_data: pd.DataFrame):
    # Mock the to_csv method to avoid file I/O
    monkeypatch.setattr(pd.DataFrame, "to_csv", lambda self, *args, **kwargs: None)
    
    result = rollup(sample_data)
    
    expected_data = {
        'hierarchy': ['1', '1.2', '1.2.3', '1.2.3.4', '1.2.3.5', '2', '2.1', '2.1.1'],
        'amount1': [30, 30, 30, 10, 20, 15, 15, 15],
        'amount2': [10, 5, 5, 2, 3, 4, 4, 4]
    }
    expected_df = pd.DataFrame(expected_data)
    
    pd.testing.assert_frame_equal(result, expected_df)