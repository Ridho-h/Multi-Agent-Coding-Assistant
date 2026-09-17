import json
import logging
import time
from pathlib import Path
from orchestrator.pipeline import run_pipeline
from tasks.task_definitions import TASKS

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

def run_evaluation(output_file: str = "metrics.json"):
    results = []
    total_tasks = len(TASKS)
    successful_tasks = 0
    total_iterations = 0
    
    start_time = time.time()
    
    for i, task in enumerate(TASKS):
        logger.info(f"--- Evaluating Task {i+1}/{total_tasks}: {task['id']} ---")
        
        try:
            pipeline_result = run_pipeline(task['spec'], max_iterations=4)
            
            if pipeline_result.success:
                successful_tasks += 1
                
            total_iterations += pipeline_result.iterations
            
            results.append({
                "id": task["id"],
                "spec": task["spec"],
                "success": pipeline_result.success,
                "iterations": pipeline_result.iterations,
                "failure_reason": pipeline_result.failure_reason,
                "code": pipeline_result.final_code
            })
        except Exception as e:
            logger.error(f"Task {task['id']} failed with exception: {e}")
            results.append({
                "id": task["id"],
                "spec": task["spec"],
                "success": False,
                "iterations": 0,
                "failure_reason": str(e),
                "code": None
            })
            
    end_time = time.time()
    
    metrics = {
        "summary": {
            "total_tasks": total_tasks,
            "successful_tasks": successful_tasks,
            "success_rate": f"{(successful_tasks / total_tasks) * 100:.1f}%",
            "average_iterations": round(total_iterations / total_tasks, 2),
            "total_time_seconds": round(end_time - start_time, 2)
        },
        "tasks": results
    }
    
    Path(output_file).write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    logger.info(f"Evaluation complete. Metrics saved to {output_file}")
    
if __name__ == "__main__":
    run_evaluation()
