# ---- AST Validation ----
# File: phpcomment/validation/ast_validator.py

import subprocess
from pathlib import Path
from tempfile import NamedTemporaryFile

def validate_code_integrity(original: str, modified: str) -> bool:
    """Verify that only comments were modified using the PHP comparator script"""
    # Create temp files for comparison
    with NamedTemporaryFile(mode='w+', suffix='.php', delete=False) as f1, \
         NamedTemporaryFile(mode='w+', suffix='.php', delete=False) as f2:
        
        f1.write(original)
        f2.write(modified)
        f1.flush()
        f2.flush()

        # Run the PHP comparator script
        result = subprocess.run(
            ['php', 'compare-php-files/compare-php-files.php', f1.name, f2.name],
            capture_output=True,
            text=True
        )

    # Clean up temp files
    Path(f1.name).unlink()
    Path(f2.name).unlink()

    # Check output for "true" (only comments changed) vs "false" (code changed)
    output = result.stdout.strip().lower()
    return output == "true"
