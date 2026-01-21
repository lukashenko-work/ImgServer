"""Dataclasses models"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional

from config import Config


@dataclass
class Image:
    id: Optional[int] = None
    filename: str = ''
    original_name: str = ''
    size: int = 0
    upload_time: Optional[datetime] = None
    file_type: str = ''

    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'filename': self.filename,
            'original_name': self.original_name,
            'size': self.size,
            'upload_time': self.upload_time,
            'file_type': self.file_type,
            'url': f'/{Config.UPLOAD_FOLDER}/{self.filename}'
        }        
