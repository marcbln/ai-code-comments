# ---- Core Processing Logic ----
# File: phpcomment/core/processor.py

import os
from pathlib import Path
from typing import Optional
from ..llm.api_client import LLMClient

import time

def process_php_file(file_path: Path, dry_run: bool = False, verbose: bool = False, model: str = "openrouter/qwen/qwen-2.5-coder-32b-instruct") -> Optional[str]:
    """Process PHP file through documentation pipeline"""
    originalCode = file_path.read_text()
    
    try:
        start_time = time.time()
        if verbose:
            print(f"⏳ Analyzing {len(originalCode)} characters...")
            
        modifiedCode = LLMClient(modelWithPrefix=model).improveDocumentation(originalCode, verbose=verbose)
        
        if verbose:
            print(f"✅ Analysis completed in {time.time() - start_time:.1f}s")
        
        if len(originalCode.splitlines()) > 100:
            print(f"Warning: Processed large file ({len(originalCode.splitlines())} lines) in chunks")
            
        if not dry_run:
            file_path.write_text(modifiedCode)
            
        return modifiedCode
    except Exception as e:
        if "Code chunk too large" in str(e):
            raise RuntimeError(
                f"Failed to process {file_path.name}: File too large even after chunking. "
                "Consider splitting the file into smaller modules."
            ) from e
        raise
