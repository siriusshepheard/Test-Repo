import yaml
import sys
import logging
from typing import Dict, List, Any
from pathlib import Path

# Configure logging
def setup_logging() -> None:
    """Configure logging with appropriate format and level."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

def validate_task(task: Dict[str, Any], task_name: str) -> List[str]:
    """Validate a pipeline task configuration."""
    errors = []
    
    if not isinstance(task, dict):
        error_msg = f"Task '{task_name}' must be a dictionary"
        logging.error(error_msg)
        errors.append(error_msg)
        return errors
    
    # Check required fields
    required_fields = ['task', 'inputs'] if 'task' in task_name.lower() else []
    for field in required_fields:
        if field not in task:
            error_msg = f"Missing required field '{field}' in task '{task_name}'"
            logging.warning(error_msg)
            errors.append(error_msg)
    
    # Validate specific tasks
    if task.get('task') == 'PublishCodeCoverageResults@1':
        warning_msg = "Warning: PublishCodeCoverageResults is deprecated. Consider using newer coverage reporting tasks."
        logging.warning(warning_msg)
        errors.append(warning_msg)
    
    # Validate AzureWebApp task
    if task.get('task') == 'AzureWebApp@1':
        required_inputs = ['azureSubscription', 'appName', 'package']
        for input_field in required_inputs:
            if input_field not in task.get('inputs', {}):
                error_msg = f"Missing required input '{input_field}' in AzureWebApp task"
                logging.error(error_msg)
                errors.append(error_msg)
    
    return errors

def validate_pipeline(yaml_content: Dict[str, Any]) -> List[str]:
    """Validate the entire pipeline configuration."""
    errors = []
    logging.info("Starting pipeline validation...")
    
    # Validate required top-level fields
    required_fields = ['trigger', 'pool']
    for field in required_fields:
        if field not in yaml_content:
            error_msg = f"Missing required field '{field}'"
            logging.error(error_msg)
            errors.append(error_msg)
    
    # Validate stages
    if 'stages' not in yaml_content:
        error_msg = "Pipeline must contain 'stages'"
        logging.error(error_msg)
        errors.append(error_msg)
        return errors
    
    stages = yaml_content['stages']
    if not isinstance(stages, list):
        error_msg = "'stages' must be a list"
        logging.error(error_msg)
        errors.append(error_msg)
        return errors
    
    # Validate each stage
    for i, stage in enumerate(stages, 1):
        logging.info(f"Validating stage {i} of {len(stages)}")
        if 'jobs' not in stage:
            error_msg = f"Stage '{stage.get('displayName', 'unnamed')}' must contain 'jobs'"
            logging.error(error_msg)
            errors.append(error_msg)
            continue
        
        # Validate jobs in stage
        for j, job in enumerate(stage['jobs'], 1):
            logging.debug(f"Validating job {j} in stage {i}")
            if isinstance(job, dict) and 'steps' in job:
                # Validate each step in the job
                for step in job['steps']:
                    step_name = step.get('displayName', 'unnamed step')
                    step_errors = validate_task(step, step_name)
                    if step_errors:
                        logging.warning(f"Found {len(step_errors)} issues in step '{step_name}'")
                        errors.extend(step_errors)
    
    return errors

def load_pipeline_file(file_path: str) -> Dict[str, Any]:
    """Load and parse the pipeline YAML file."""
    pipeline_path = Path(file_path)
    
    if not pipeline_path.exists():
        raise FileNotFoundError(f"Pipeline file not found at: {pipeline_path.absolute()}")
    
    if not pipeline_path.is_file():
        raise ValueError(f"Path exists but is not a file: {pipeline_path.absolute()}")
    
    try:
        with pipeline_path.open('r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise yaml.YAMLError(f"Failed to parse YAML file: {e}")
    except UnicodeDecodeError as e:
        raise UnicodeDecodeError(f"Failed to read file - encoding error: {e}")

def main():
    setup_logging()
    logging.info("Starting pipeline validation script")
    
    try:
        pipeline_content = load_pipeline_file('azure-pipelines.yml')
        logging.info("Successfully loaded azure-pipelines.yml")
        
        errors = validate_pipeline(pipeline_content)
        
        if errors:
            logging.error(f"Validation found {len(errors)} issues")
            print("\nValidation found the following issues:")
            for error in errors:
                print(f"- {error}")
            sys.exit(1)
        else:
            logging.info("Validation completed successfully with no issues")
            print("\nValidation successful! No issues found.")
            sys.exit(0)
            
    except FileNotFoundError as e:
        logging.critical(f"File error: {e}")
        print(f"Error: {e}")
        sys.exit(1)
    except yaml.YAMLError as e:
        logging.critical(f"YAML parsing error: {e}")
        print(f"Error parsing YAML file: {e}")
        sys.exit(1)
    except UnicodeDecodeError as e:
        logging.critical(f"File encoding error: {e}")
        print(f"Error reading file: {e}")
        sys.exit(1)
    except Exception as e:
        logging.critical(f"Unexpected error: {e}", exc_info=True)
        print(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 