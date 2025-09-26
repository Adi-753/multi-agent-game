from abc import ABC, abstractmethod
from typing import Any, Dict, List
import logging

class BaseAgent(ABC):
    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(name)
        
    @abstractmethod
    async def execute(self, *args, **kwargs) -> Any:
        pass
    
    def log(self, message: str, level: str = "info"):
        getattr(self.logger, level)(f"[{self.name}] {message}")