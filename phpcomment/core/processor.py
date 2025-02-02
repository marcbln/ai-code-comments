# ---- Core Processing Logic ----
# File: phpcomment/core/processor.py

import os
import tempfile
import subprocess
import shutil
from pathlib import Path
from typing import Optional
from ..llm.api_client import LLMClient
from ..llm.prompts import DocumentationPrompts
from ..strategies import WholeFileStrategy, UDiffStrategy, ChangeStrategy

import time

def validate_php_code(pathOriginalFile: Path, pathModifiedCodeTempFile: Path) -> bool:
    
    try:
        # Get path to comparison script
        compare_script = Path(__file__).parent.parent.parent / 'compare-php-files' / 'compare-php-files.php'
        
        if not compare_script.exists():
            raise RuntimeError(f"Comparison script not found at {compare_script}")
        
        print(f"🔍 Validating code changes...")
            
        # Run comparison
        cmd = ['php', str(compare_script), str(pathOriginalFile), str(pathModifiedCodeTempFile)]
        print(f"🚀 Running command: {' '.join(cmd)}")
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print(f"Error running comparison script: {result.stderr}")
            return False
            
        is_valid = result.stdout.strip() == 'true'
        
        if is_valid:
            print("✅ Code validation passed")
            return True
        else:
            print("❌ Code validation failed - functionality changed")

            # Show colored diff
            diff_result = subprocess.run(
                ['diff', '--color=always', str(pathOriginalFile), str(pathModifiedCodeTempFile)],
                capture_output=True,
                text=True
            )
            if diff_result.stdout or diff_result.stderr:
                print("\nDifferences found:")
                print(diff_result.stdout or diff_result.stderr)

            print(f">>>> original_file: {str(pathOriginalFile)}")
            print(f">>>> modified_file: {str(pathModifiedCodeTempFile)}")

            return False
    except Exception as e:
        print(f"Validation error: {str(e)}")
        return False

def improveDocumentationOfPhpFile(pathOrigFile: Path, verbose: bool = False,
                                  model: str = "openrouter/qwen/qwen-2.5-coder-32b-instruct",
                                  strategy: ChangeStrategy = WholeFileStrategy()) -> None:
    """Process PHP file through documentation pipeline"""
    originalCode = pathOrigFile.read_text()

    try:
        start_time = time.time()
        print(f"⏳ Analyzing {len(originalCode)} characters...")
        
        # ---- send prompt to LLM ----
        systemPrompt, userPrompt = DocumentationPrompts.get_full_prompt(originalCode, strategy)
        llmResponseRaw = LLMClient(modelWithPrefix=model).sendRequest(systemPrompt, userPrompt)
        print(f"✅ LLM request completed in {time.time() - start_time:.1f}s")
        print(f">>>> LLM Response Raw:\n\n{llmResponseRaw}")

        # Apply changes using strategy (wholefile or udiff)
        pathModifiedCodeTempFile = strategy.process_llm_response(llmResponseRaw, pathOrigFile)
        if pathModifiedCodeTempFile is None:
            print(f"⚠️ No changes were made to the file")
            return


        print(f"✅ Temp file {pathModifiedCodeTempFile} was created.")
        
        # Validate the changes
        is_valid = validate_php_code(pathOrigFile, pathModifiedCodeTempFile)
        if not is_valid:


            raise RuntimeError(
                f"Failed to process {pathOrigFile.name}: Code validation failed. "
                "The changes would alter the code functionality."
            )

        if pathModifiedCodeTempFile and pathModifiedCodeTempFile.exists():
            # Handle diff output format
            if strategy == UDiffStrategy():
                diff_result = subprocess.run(
                    ['diff', '-u', '--color=always', str(pathOrigFile), str(pathModifiedCodeTempFile)],
                    capture_output=True,
                    text=True
                )
            else:
                # Show standard diff of changes
                diff_result = subprocess.run(
                    ['diff', '--color=always', str(pathOrigFile), str(pathModifiedCodeTempFile)],
                    capture_output=True,
                    text=True
                )
            if diff_result.stdout or diff_result.stderr:
                print("\n✅ Applied changes:")
                print(diff_result.stdout or diff_result.stderr)
                # Copy the validated temporary file to the target location
                shutil.copy2(pathModifiedCodeTempFile, pathOrigFile)
            else:
                print("\n⚠️ No changes were made to the file")
            
            pathModifiedCodeTempFile.unlink()  # Clean up temp file after successful copy
        else:
            raise RuntimeError("Temporary file not found after validation")
        
        return None
    except Exception as e:
        if "Code chunk too large" in str(e):
            raise RuntimeError(
                f"Failed to process {pathOrigFile.name}: File too large even after chunking. "
                "Consider splitting the file into smaller modules."
            ) from e
        raise
