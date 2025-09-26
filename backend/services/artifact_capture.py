import os
import json
import base64
from datetime import datetime
from typing import Dict, List
import aiofiles

class ArtifactCapture:
    def __init__(self):
        self.artifacts_dir = "artifacts"
        self._ensure_directories()
    
    def _ensure_directories(self):
        subdirs = ["screenshots", "dom_snapshots", "logs", "network"]
        for subdir in subdirs:
            os.makedirs(os.path.join(self.artifacts_dir, subdir), exist_ok=True)
    
    async def save_screenshot(self, screenshot_data: bytes, test_id: str, step: str) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{test_id}_{step}_{timestamp}.png"
        filepath = os.path.join(self.artifacts_dir, "screenshots", filename)
        
        async with aiofiles.open(filepath, 'wb') as f:
            await f.write(screenshot_data)
        
        return filepath
    
    async def save_dom_snapshot(self, dom_content: str, test_id: str, step: str) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{test_id}_{step}_{timestamp}.html"
        filepath = os.path.join(self.artifacts_dir, "dom_snapshots", filename)
        
        async with aiofiles.open(filepath, 'w') as f:
            await f.write(dom_content)
        
        return filepath
    
    async def save_logs(self, logs: List[Dict], test_id: str, log_type: str = "console") -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{test_id}_{log_type}_{timestamp}.json"
        filepath = os.path.join(self.artifacts_dir, "logs", filename)
        
        async with aiofiles.open(filepath, 'w') as f:
            await f.write(json.dumps(logs, indent=2))
        
        return filepath
    
    async def save_network_capture(self, network_data: List[Dict], test_id: str) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{test_id}_network_{timestamp}.json"
        filepath = os.path.join(self.artifacts_dir, "network", filename)
        
        async with aiofiles.open(filepath, 'w') as f:
            await f.write(json.dumps(network_data, indent=2))
        
        return filepath
    
    def get_artifact_summary(self, test_id: str) -> Dict:
        summary = {
            "screenshots": [],
            "dom_snapshots": [],
            "logs": [],
            "network_captures": []
        }
        
        for subdir, key in [
            ("screenshots", "screenshots"),
            ("dom_snapshots", "dom_snapshots"),
            ("logs", "logs"),
            ("network", "network_captures")
        ]:
            dir_path = os.path.join(self.artifacts_dir, subdir)
            if os.path.exists(dir_path):
                for file in os.listdir(dir_path):
                    if file.startswith(test_id):
                        summary[key].append(os.path.join(dir_path, file))
        
        return summary