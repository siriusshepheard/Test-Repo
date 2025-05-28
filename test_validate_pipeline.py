import pytest
from validate_pipeline import validate_pipeline  # Adjust based on your script's function name

def test_validate_pipeline_valid():
    """Test validate_pipeline with a valid YAML file."""
    with open("test_valid.yaml", "w", encoding="utf-8") as f:
        f.write("key: value\n")
    assert validate_pipeline("test_valid.yaml") == True

def test_validate_pipeline_invalid():
    """Test validate_pipeline with an invalid YAML file."""
    with open("test_invalid.yaml", "w", encoding="utf-8") as f:
        f.write("key: [value\n")  # Missing closing bracket
    assert validate_pipeline("test_invalid.yaml") == False

def test_validate_pipeline_empty_file():
    """Test validate_pipeline with an empty YAML file."""
    with open("test_empty.yaml", "w", encoding="utf-8") as f:
        f.write("")
    assert validate_pipeline("test_empty.yaml") == False

def test_validate_pipeline_non_existent_file():
    """Test validate_pipeline with a non-existent file."""
    assert validate_pipeline("non_existent.yaml") == False