# ---- Core Processing Logic ----
# File: phpcomment/core/processor.py

import os
from pathlib import Path
from typing import Optional
from ..llm.api_client import LLMClient

def process_php_file(file_path: Path, dry_run: bool = False) -> Optional[str]:
    """Process PHP file through documentation pipeline"""
    original = file_path.read_text()
    modified = LLMClient().generate_documentation(original)
    
    if not dry_run:
        file_path.write_text(modified)
    
    return modified
