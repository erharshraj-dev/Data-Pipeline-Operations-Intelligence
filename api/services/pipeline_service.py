import time
import json
import os
from workflows.main import main


class PipelineService:

    @staticmethod
    def execute():
        start_time = time.time()
        try:
            result = main()
            end_time = time.time()
            execution_time = round(end_time - start_time, 2)
            
            # Save execution metadata
            metadata = {
                "status": "SUCCESS",
                "execution_time": execution_time
            }
            os.makedirs("output", exist_ok=True)
            with open("output/execution_metadata.json", "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=4)
                
            return result
        except Exception as e:
            end_time = time.time()
            execution_time = round(end_time - start_time, 2)
            metadata = {
                "status": "FAILED",
                "execution_time": execution_time,
                "error": str(e)
            }
            os.makedirs("output", exist_ok=True)
            with open("output/execution_metadata.json", "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=4)
            raise e