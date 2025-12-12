import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

from datetime import datetime
import pkgutil

import CAI_pkg

class ModuleFilter(logging.Filter):
    def __init__(self, allowed_modules):
        super().__init__()
        self.allowed = allowed_modules

    def filter(self, record):
        return record.name in self.allowed

def init_logger():
    allowed_modules = [m.name for m in pkgutil.walk_packages(CAI_pkg.__path__, CAI_pkg.__name__ + ".")]

    # log filename
    date = datetime.now().strftime("%m-%d-%Y_%H:%M:%S")
    filename = f'tmp/logs/log__{date}.log' 
    
    handler = logging.FileHandler(filename, encoding='utf-8')
    handler.setLevel(logging.INFO)
    handler.addFilter(ModuleFilter(allowed_modules))

    # Remove other handlers if present
    root_logger = logging.getLogger()
    root_logger.handlers = []
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.INFO)