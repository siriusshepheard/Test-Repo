import yaml
import sys
from typing import Dict, List, Any

def validate_task(task: Dict[str, Any], task_name: str) -> List[str]:
    """Validate a pipeline task configuration."""
    errors = []
    
    if not isinstance(task, dict):
        errors.append(f"Task '{task_name}' must be a dictionary")
        return errors
    
    # Check required fields
    required_fields = ['task', 'inputs'] if 'task' in task_name.lower() else []
    for field in required_fields:
        if field not in task:
            errors.append(f"Missing required field '{field}' in task '{task_name}'")
    
    # Validate specific tasks
    if task.get('task') == 'PublishCodeCoverageResults@1':
        errors.append("Warning: PublishCodeCoverageResults is deprecated. Consider using newer coverage reporting tasks.")
    
    # Validate AzureWebApp task
    if task.get('task') == 'AzureWebApp@1':
        required_inputs = ['azureSubscription', 'appName', 'package']
        for input_field in required_inputs:
            if input_field not in task.get('inputs', {}):
                errors.append(f"Missing required input '{input_field}' in AzureWebApp task")
    
    return errors

def validate_pipeline(yaml_content: Dict[str, Any]) -> List[str]:
    """Validate the entire pipeline configuration."""
    errors = []
    
    # Validate required top-level fields
    required_fields = ['trigger', 'pool']
    for field in required_fields:
        if field not in yaml_content:
            errors.append(f"Missing required field '{field}'")
    
    # Validate stages
    if 'stages' not in yaml_content:
        errors.append("Pipeline must contain 'stages'")
        return errors
    
    stages = yaml_content['stages']
    if not isinstance(stages, list):
        errors.append("'stages' must be a list")
        return errors
    
    # Validate each stage
    for stage in stages:
        if 'jobs' not in stage:
            errors.append(f"Stage '{stage.get('displayName', 'unnamed')}' must contain 'jobs'")
            continue
        
        # Validate jobs in stage
        for job in stage['jobs']:
            if isinstance(job, dict) and 'steps' in job:
                # Validate each step in the job
                for step in job['steps']:
                    step_name = step.get('displayName', 'unnamed step')
                    errors.extend(validate_task(step, step_name))
    
    return errors

def main():
    try:
        with open('azure-pipelines.yml', 'r') as f:
            pipeline_content = yaml.safe_load(f)
        
        print("Validating azure-pipelines.yml...")
        errors = validate_pipeline(pipeline_content)
        
        if errors:
            print("\nValidation found the following issues:")
            for error in errors:
                print(f"- {error}")
            sys.exit(1)
        else:
            print("\nValidation successful! No issues found.")
            sys.exit(0)
            
    except yaml.YAMLError as e:
        print(f"Error parsing YAML file: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("Error: azure-pipelines.yml not found")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 