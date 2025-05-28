import pytest
from validate_pipeline import validate_pipeline  # Adjust based on your script's function name

def test_validate_pipeline_valid():
    """Test validate_pipeline with a valid YAML file."""
    valid_pipeline = """
trigger:
  - main
pool:
  vmImage: 'ubuntu-latest'
stages:
  - stage: Build
    jobs:
      - job: BuildJob
        steps:
          - task: UsePythonVersion@0
            inputs:
              versionSpec: '3.x'
"""
    with open("test_valid.yaml", "w", encoding="utf-8") as f:
        f.write(valid_pipeline)
    # Check that there are no validation errors
    assert len(validate_pipeline("test_valid.yaml")) == 0

def test_validate_pipeline_invalid():
    """Test validate_pipeline with an invalid YAML file - missing required fields."""
    invalid_pipeline = """
stages:  # Missing trigger and pool
  - stage: Build
    jobs:
      - job: BuildJob
        steps:
          - task: UsePythonVersion@0
            inputs:
              versionSpec: '3.x'
"""
    with open("test_invalid.yaml", "w", encoding="utf-8") as f:
        f.write(invalid_pipeline)
    # Check that there are validation errors
    errors = validate_pipeline("test_invalid.yaml")
    assert len(errors) > 0
    assert "Missing required field 'trigger'" in errors
    assert "Missing required field 'pool'" in errors

def test_validate_pipeline_empty_file():
    """Test validate_pipeline with an empty YAML file."""
    with open("test_empty.yaml", "w", encoding="utf-8") as f:
        f.write("")
    # Check that there are validation errors
    errors = validate_pipeline("test_empty.yaml")
    assert len(errors) > 0

def test_validate_pipeline_non_existent_file():
    """Test validate_pipeline with a non-existent file."""
    # Check that there are validation errors
    errors = validate_pipeline("non_existent.yaml")
    assert len(errors) > 0