# tests/test_pipeline.py
import pandas as pd
import pytest
from pipeline import preprocess_data

def test_preprocess_data():
    df = pd.DataFrame({
        "age": ["[70-80)"],
        "gender": ["Male"],
        "race": ["Caucasian"],
        "time_in_hospital": [5],
        "num_lab_procedures": [40],
        "num_medications": [15],
        "diabetesMed": ["Yes"],
        "readmitted": ["<30"]
    })
    X, y = preprocess_data(df)
    assert X.shape[1] == 7
    assert y[0] == 1
