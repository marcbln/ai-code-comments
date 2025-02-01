# ---- Core Processing Logic ----
# File: phpcomment/core/processor.py

import os
import tempfile
import subprocess
import shutil
from pathlib import Path
from typing import Optional
from ..llm.api_client import LLMClient

import time

def validate_php_code(original_file: Path, modified_code: str, verbose: bool = False) -> tuple[bool, Optional[Path]]:
    """Validate that the modified PHP code maintains the same functionality"""
    # Create temporary file for modified code
    tmp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.php', delete=False)
    tmp_path = Path(tmp_file.name)
    tmp_file.write(modified_code)
    tmp_file.close()
    
    try:
        # Get path to comparison script
        compare_script = Path(__file__).parent.parent.parent / 'compare-php-files' / 'compare-php-files.php'
        
        if not compare_script.exists():
            raise RuntimeError(f"Comparison script not found at {compare_script}")
        
        if verbose:
            print(f"🔍 Validating code changes...")
            
        # Run comparison
        result = subprocess.run(
            ['php', str(compare_script), str(original_file), str(tmp_path)],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print(f"Error running comparison script: {result.stderr}")
            return False, None
            
        is_valid = result.stdout.strip() == 'true'
        
        if is_valid:
            if verbose:
                print("✅ Code validation passed")
            return True, tmp_path
        else:
            print("❌ Code validation failed - functionality changed")

            # Show colored diff
            diff_result = subprocess.run(
                ['diff', '--color=always', str(original_file), str(tmp_path)],
                capture_output=True,
                text=True
            )
            if diff_result.stdout or diff_result.stderr:
                print("\nDifferences found:")
                print(diff_result.stdout or diff_result.stderr)

            print(f">>>> original_file: {str(original_file)}")
            print(f">>>> modified_file: {str(tmp_path)}")

            return False, None
    except Exception as e:
        print(f"Validation error: {str(e)}")
        return False, None

def process_php_file(file_path: Path, dry_run: bool = False, verbose: bool = False, 
                    model: str = "openrouter/qwen/qwen-2.5-coder-32b-instruct",
                    diff_format: bool = False) -> Optional[str]:
    """Process PHP file through documentation pipeline"""
    originalCode = file_path.read_text()
    
    try:
        start_time = time.time()
        if verbose:
            print(f"⏳ Analyzing {len(originalCode)} characters...")
            
        llmResponse = LLMClient(modelWithPrefix=model).improveDocumentation(originalCode, diff_format=diff_format, verbose=verbose)
        print(f">>>> diff_format: {diff_format}")
        print(f">>>> llmResponse:\n\n{llmResponse}\n\n") # fixme

        if verbose:
            print(f"✅ LLM request completed in {time.time() - start_time:.1f}s ({len(llmResponse)} characters)")
        
        # if len(originalCode.splitlines()) > 100:
        #     print(f"Warning: Processed large file ({len(originalCode.splitlines())} lines) in chunks")
        # Handle diff format
        if diff_format:
            # Create patch file
            patch_file = tempfile.NamedTemporaryFile(mode='w', suffix='.diff', delete=False)
            patch_path = Path(patch_file.name)
            patch_file.write(llmResponse)
            patch_file.close()

            if verbose:
                print(f"The LLM returned the following diff patch: {patch_path.absolute()} ...")
                # print(llmResponse)

            # Apply patch
            try:
                cmd = ['patch', str(file_path), str(patch_path)]
                if verbose:
                    print(f"🔧 Applying patch: {' '.join(cmd)}")
                subprocess.run(
                    cmd,
                    check=True,
                    capture_output=True
                )
            except subprocess.CalledProcessError as e:
                raise RuntimeError(f"Failed to apply patch: {e.stderr.decode()}") from e
#            finally:
#                patch_path.unlink()
            
            # Read back patched file for validation
            llmResponse = file_path.read_text()
        
        # Validate the changes
        is_valid, tmp_path = validate_php_code(file_path, llmResponse, verbose)
        if not is_valid:

            print(f"\n\nmodified code:\n\n{llmResponse}")

            raise RuntimeError(
                f"Failed to process {file_path.name}: Code validation failed. "
                "The changes would alter the code functionality."
            )

        if not dry_run:
            if tmp_path and tmp_path.exists():
                # Handle diff output format
                if diff_format:
                    diff_result = subprocess.run(
                        ['diff', '-u', '--color=always', str(file_path), str(tmp_path)],
                        capture_output=True,
                        text=True
                    )
                else:
                    # Show standard diff of changes
                    diff_result = subprocess.run(
                        ['diff', '--color=always', str(file_path), str(tmp_path)],
                        capture_output=True,
                        text=True
                    )
                if diff_result.stdout or diff_result.stderr:
                    print("\n✅ Applied changes:")
                    print(diff_result.stdout or diff_result.stderr)
                    # Copy the validated temporary file to the target location
                    shutil.copy2(tmp_path, file_path)
                else:
                    print("\n⚠️ No changes were made to the file")
                
                tmp_path.unlink()  # Clean up temp file after successful copy
            else:
                raise RuntimeError("Temporary file not found after validation")
            
        # Only return the modified code in dry-run mode
        if dry_run:
            return llmResponse
        return None
    except Exception as e:
        if "Code chunk too large" in str(e):
            raise RuntimeError(
                f"Failed to process {file_path.name}: File too large even after chunking. "
                "Consider splitting the file into smaller modules."
            ) from e
        raise
