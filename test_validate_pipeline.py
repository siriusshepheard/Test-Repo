import pytest
import os
from validate_pipeline import validate_pipeline, load_pipeline_file

@pytest.fixture(autouse=True)
def cleanup():
    """Clean up temporary files after each test."""
    yield
    # Clean up after test
    test_files = [
        "test_valid.yaml",
        "test_invalid.yaml",
        "test_empty.yaml",
        "test_empty_jobs.yaml",
        "test_invalid_job.yaml",
        "test_missing_steps.yaml"
    ]
    for file in test_files:
        if os.path.exists(file):
            os.remove(file)

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
    yaml_content = load_pipeline_file("test_valid.yaml")
    assert len(validate_pipeline(yaml_content)) == 0

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
    yaml_content = load_pipeline_file("test_invalid.yaml")
    errors = validate_pipeline(yaml_content)
    assert len(errors) > 0
    assert "Missing required field 'trigger'" in errors
    assert "Missing required field 'pool'" in errors

def test_validate_pipeline_empty_file():
    """Test validate_pipeline with an empty YAML file."""
    with open("test_empty.yaml", "w", encoding="utf-8") as f:
        f.write("")
    yaml_content = load_pipeline_file("test_empty.yaml")
    errors = validate_pipeline(yaml_content)
    assert len(errors) > 0

def test_validate_pipeline_non_existent_file():
    """Test validate_pipeline with a non-existent file."""
    yaml_content = load_pipeline_file("non_existent.yaml")
    errors = validate_pipeline(yaml_content)
    assert len(errors) > 0

def test_validate_pipeline_empty_jobs():
    """Test validate_pipeline with a stage containing empty jobs list."""
    invalid_pipeline = """
trigger:
  - main
pool:
  vmImage: 'ubuntu-latest'
stages:
  - stage: Build
    jobs: []
"""
    with open("test_empty_jobs.yaml", "w", encoding="utf-8") as f:
        f.write(invalid_pipeline)
    yaml_content = load_pipeline_file("test_empty_jobs.yaml")
    errors = validate_pipeline(yaml_content)
    assert len(errors) > 0
    assert any("must contain at least one job" in error for error in errors)

def test_validate_pipeline_invalid_job_structure():
    """Test validate_pipeline with invalid job structure."""
    invalid_pipeline = """
trigger:
  - main
pool:
  vmImage: 'ubuntu-latest'
stages:
  - stage: Build
    jobs:
      - "invalid_job"  # Should be a dictionary
"""
    with open("test_invalid_job.yaml", "w", encoding="utf-8") as f:
        f.write(invalid_pipeline)
    yaml_content = load_pipeline_file("test_invalid_job.yaml")
    errors = validate_pipeline(yaml_content)
    assert len(errors) > 0
    assert any("must be a dictionary" in error for error in errors)

def test_validate_pipeline_missing_steps():
    """Test validate_pipeline with a job missing steps field."""
    invalid_pipeline = """
trigger:
  - main
pool:
  vmImage: 'ubuntu-latest'
stages:
  - stage: Build
    jobs:
      - job: BuildJob
        # Missing steps field
"""
    with open("test_missing_steps.yaml", "w", encoding="utf-8") as f:
        f.write(invalid_pipeline)
    yaml_content = load_pipeline_file("test_missing_steps.yaml")
    errors = validate_pipeline(yaml_content)
    assert len(errors) > 0
    assert any("must contain 'steps'" in error for error in errors)