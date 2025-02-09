# ---- Core Processing Logic ----
# File: phpcomment/core/processor.py

import shutil
import subprocess
import time
from pathlib import Path

from ..llm.api_client import LLMClient
from ..llm.prompts import DocumentationPrompts
from ..strategies import UDiffStrategy, ChangeStrategy
from ..utils.logger import logger


def validate_php_code(pathOriginalFile: Path, pathModifiedCodeTempFile: Path) -> bool:
    
    try:
        # Get path to comparison script
        compare_script = Path(__file__).parent.parent.parent / 'compare-php-files' / 'compare-php-files.php'
        
        if not compare_script.exists():
            raise RuntimeError(f"Comparison script not found at {compare_script}")
        

        logger.info("Validating code changes...")
            
        # Run comparison
        cmd = ['php', str(compare_script), str(pathOriginalFile), str(pathModifiedCodeTempFile)]
        logger.debug(f"Running command: {' '.join(cmd)}")
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            logger.error(f"Error running comparison script: {result.stderr}")
            return False
            
        is_valid = result.stdout.strip() == 'true'
        
        if is_valid:
            logger.success("Code validation passed")
            return True
        else:
            logger.error("Code validation failed - functionality changed")

            # Show colored diff
            diff_result = subprocess.run(
                ['diff', '--color=always', str(pathOriginalFile), str(pathModifiedCodeTempFile)],
                capture_output=True,
                text=True
            )
            if diff_result.stdout or diff_result.stderr:
                logger.warning("Differences found:")
                print(diff_result.stdout or diff_result.stderr)

            logger.debug(f"Original file: {str(pathOriginalFile)}")
            logger.debug(f"Modified file: {str(pathModifiedCodeTempFile)}")

            return False
    except Exception as e:
        logger.error(f"Validation error: {str(e)}")
        return False

def improveDocumentationOfPhpFile(pathOrigFile: Path,
                                  model: str,
                                  strategy: ChangeStrategy) -> None:
    """Process PHP file through documentation pipeline"""
    originalCode = pathOrigFile.read_text()

    try:
        start_time = time.time()
        logger.info(f"⏳ Analyzing {len(originalCode)} characters...")
        
        # ---- send prompt to LLM ----
        systemPrompt, userPrompt = DocumentationPrompts.get_full_prompt(originalCode, strategy)
        llmResponseRaw = LLMClient(modelWithPrefix=model).sendRequest(systemPrompt, userPrompt)
        logger.success(f"LLM request completed in {time.time() - start_time:.1f}s")
        logger.debug(f"LLM Response Raw:\n\n{llmResponseRaw}", highlight=False)

        # Apply changes using strategy (wholefile or udiff)
        pathModifiedCodeTempFile = strategy.process_llm_response(llmResponseRaw, pathOrigFile)
        if pathModifiedCodeTempFile is None:
            logger.warning("No changes were made to the file")
            return


        logger.success(f"Temp file {pathModifiedCodeTempFile} was created.")
        
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
                    ['diff', '-u', '--color=always', str(pathOrigFile), str(pathModifiedCodeTempFile)],
                    capture_output=True,
                    text=True
                )
            if diff_result.stdout or diff_result.stderr:
                logger.success("Applied changes:")
                print(diff_result.stdout or diff_result.stderr)
                # same permissions as original file
                shutil.copystat(pathOrigFile, pathModifiedCodeTempFile)
                # Copy the validated temporary file to the target location
                shutil.copy2(pathModifiedCodeTempFile, pathOrigFile)
            else:
                logger.warning("No changes were made to the file")
            
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
