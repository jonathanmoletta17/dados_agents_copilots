import logging
import os
import re
from datetime import datetime
from typing import Optional

class SyncLogger:
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = os.path.join(log_dir, f"sync_logs_{timestamp}.log")
        
        self.logger = logging.getLogger("GLPISync")
        self.logger.setLevel(logging.DEBUG)
        
        # File handler
        fh = logging.FileHandler(self.log_file, encoding='utf-8')
        fh.setLevel(logging.DEBUG)
        
        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)
        
        self.sensitive_patterns = [
            (r'(App-Token: )([^\s]+)', r'\1[MASKED]'),
            (r'(Session-Token: )([^\s]+)', r'\1[MASKED]'),
            (r'(Authorization: user_token )([^\s]+)', r'\1[MASKED]'),
            (r'(user_token=)([^\s&]+)', r'\1[MASKED]'),
            (r'(app_token=)([^\s&]+)', r'\1[MASKED]')
        ]

    def _mask_sensitive_data(self, message: str) -> str:
        if not isinstance(message, str):
            return str(message)
        for pattern, replacement in self.sensitive_patterns:
            message = re.sub(pattern, replacement, message, flags=re.IGNORECASE)
        return message

    def log(self, level: str, message: str, extra: Optional[dict] = None):
        masked_message = self._mask_sensitive_data(message)
        if extra:
            masked_extra = self._mask_sensitive_data(str(extra))
            masked_message += f" | Details: {masked_extra}"
            
        if level.lower() == 'info':
            self.logger.info(masked_message)
        elif level.lower() == 'error':
            self.logger.error(masked_message)
        elif level.lower() == 'warning':
            self.logger.warning(masked_message)
        elif level.lower() == 'debug':
            self.logger.debug(masked_message)
            
    def info(self, msg: str, extra: Optional[dict] = None):
        self.log('info', msg, extra)
        
    def error(self, msg: str, extra: Optional[dict] = None):
        self.log('error', msg, extra)
        
    def warning(self, msg: str, extra: Optional[dict] = None):
        self.log('warning', msg, extra)
        
    def debug(self, msg: str, extra: Optional[dict] = None):
        self.log('debug', msg, extra)

# Global instance
sync_logger = SyncLogger()
