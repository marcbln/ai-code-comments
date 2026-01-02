### Implementation Plan: Add Twig File Commenting Support

This plan details the steps required to integrate Twig file processing into the `aicoder` tool. The core of this extension is a new PHP-based AST comparison script for Twig, which will be called by the existing Python application to ensure code integrity.

---

### Phase 1: Create the Twig AST Comparison Tool

This phase establishes the backend validation script that will compare two Twig files for syntactical equivalence, ignoring comments.

1.  **Create the Project Directory**
    Create a new directory in the project root named `compare-twig-files`.

2.  **Define Composer Dependencies**
    Create a `composer.json` file inside the `compare-twig-files` directory to manage the `twig/twig` dependency.

    **File:** `compare-twig-files/composer.json`
    ```json
    {
        "require": {
            "twig/twig": "^3.0"
        },
        "autoload": {
            "psr-4": {
                "App\\Twig\\": "src/"
            }
        }
    }
    ```

3.  **Implement the AST Comparator Logic**
    Create a `src` subdirectory within `compare-twig-files` and add the PHP class responsible for the AST comparison.

    **File:** `compare-twig-files/src/TwigAstComparator.php`
    ```php
    <?php

    namespace App\Twig;

    use Twig\Environment;
    use Twig\Error\SyntaxError;
    use Twig\Loader\FilesystemLoader;
    use Twig\Node\Node;

    class TwigAstComparator
    {
        private Environment $twig;

        public function __construct()
        {
            // Use a generic loader that can access files from the root directory.
            $loader = new FilesystemLoader('/');
            $this->twig = new Environment($loader);
        }

        private function getAst(string $filename): Node
        {
            $source = $this->twig->getLoader()->getSourceContext($filename);
            return $this->twig->parse($this->twig->tokenize($source));
        }

        public function compare(string $file1, string $file2): bool
        {
            try {
                $ast1 = $this->getAst($file1);
                $ast2 = $this->getAst($file2);
                return $this->areNodesEqual($ast1, $ast2);
            } catch (SyntaxError $e) {
                // A syntax error means the files are not syntactically equivalent.
                error_log("Syntax error during Twig comparison: " . $e->getMessage());
                return false;
            }
        }

        private function areNodesEqual(Node $node1, Node $node2): bool
        {
            if (get_class($node1) !== get_class($node2)) {
                return false;
            }

            if ($node1->getAttributes() !== $node2->getAttributes()) {
                return false;
            }

            if (count($node1) !== count($node2)) {
                return false;
            }

            foreach ($node1 as $key => $childNode1) {
                if (!$node2->hasNode($key)) {
                    return false;
                }
                $childNode2 = $node2->getNode($key);
                if (!$this->areNodesEqual($childNode1, $childNode2)) {
                    return false;
                }
            }

            return true;
        }
    }
    ```

4.  **Create the CLI Entry Point Script**
    Create the main executable PHP script in the `compare-twig-files` directory. This script will be called by the Python application.

    **File:** `compare-twig-files/compare-twig-files.php`
    ```php
    <?php

    require __DIR__.'/vendor/autoload.php';

    use App\Twig\TwigAstComparator;

    function main(string $file1, string $file2): bool
    {
        $comparator = new TwigAstComparator();
        return $comparator->compare($file1, $file2);
    }

    if ($argc !== 3) {
        fwrite(STDERR, "Usage: php compare-twig-files.php <file1> <file2>\n");
        exit(1);
    }

    echo main($argv[1], $argv[2]) ? 'true' : 'false';
    echo "\n";
    ```

5.  **Install PHP Dependencies**
    Execute the following command in your terminal from the `compare-twig-files` directory:
    ```bash
    composer install
    ```

---

### Phase 2: Integrate Twig Support into the Python Application

This phase modifies the core Python logic to recognize `.twig` files, use the appropriate LLM prompts, and call the new validator.

1.  **Add Twig-Specific LLM Prompts**
    Update `aicoder/llm/prompts.py` to include a new class with instructions tailored for documenting Twig templates.

    **File:** `aicoder/llm/prompts.py`
    ```python
    from textwrap import dedent
    from typing import Any

    from aicoder.strategies import ChangeStrategy


    class DocumentationPrompts:
        """Contains prompt templates for documentation generation"""

        SYSTEM_PROMPT = "You are a senior PHP developer. You are tasked to improve the quality of a legacy php codebase by adding or improving comments (docblocks and section comments)."

        @classmethod
        def get_full_prompt(cls, php_code: str, strategy: ChangeStrategy) -> tuple[str, str]:
            """Return complete prompt with all original rules and formatting"""
            user_prompt = dedent(f"""
                Improve the PHP_CODE by adding or improving comments (docblocks and section comments). Apply the following rules:

                - Each class should have a docblock explaining what the class does. If a docblock already exists, try to improve it.
                - Each method should have a docblock explaining what the method does, except setters and getters.
                - Do NOT add redundant PHPDoc tags to docblocks, e.g. `@return void` or `@param string $foo` without any additional information.
                - inside functions use section comments, starting with `// ----`, explaining key parts of the code, if needed.
                - in big switch-case statements, add a section comment (starting with // ----) for each case.
                - Keep ALL original code except documentation, do NOT add or remove any code. only comments.
                - NEVER replace code with comments like "// ... rest of the code remains unchanged ..."
                - do NOT change or remove timestamp comments like "07/2024 created"
                - do NOT remove comments that mark the main entry point, usually "==== MAIN ===="
                - do NOT remove TODO and FIXME comments
                - do NOT add comments to getters and setters"
                """)

            # Add strategy-specific prompt additions
            user_prompt += strategy.get_prompt_additions()
            
            user_prompt += f"\n\nPHP_CODE:\n{php_code}\n"

            return cls.SYSTEM_PROMPT, user_prompt


    class TwigDocumentationPrompts:
        """Contains prompt templates for Twig documentation generation."""

        SYSTEM_PROMPT = "You are a senior frontend developer specializing in Twig templates. You are tasked to improve the quality of a legacy Twig codebase by adding or improving comments."

        @classmethod
        def get_full_prompt(cls, twig_code: str, strategy: ChangeStrategy) -> tuple[str, str]:
            """Return complete prompt for Twig files."""
            user_prompt = dedent(f"""
                Improve the TWIG_CODE by adding or improving comments. Apply the following rules:

                - Add comments using `{{{{# ... #}}}}` to explain complex logic, loops, or variable assignments.
                - Keep ALL original code except for the comments. Do NOT add, remove, or change any Twig logic, variables, or HTML structure.
                - NEVER replace code with comments like `{{{{# ... rest of the code remains unchanged ... #}}}}`.
                - Your task is to add documentation, not to refactor or change functionality.
                """)

            user_prompt += strategy.get_prompt_additions()
            user_prompt += f"\n\nTWIG_CODE:\n{twig_code}\n"

            return cls.SYSTEM_PROMPT, user_prompt
    ```

2.  **Generalize the Core Processor and Validator**
    Refactor `aicoder/core/processor.py` to handle different file types. Rename `improveDocumentationOfPhpFile` to a more generic `improve_file_documentation` and create a dispatcher for validation scripts.

    **File:** `aicoder/core/processor.py`
    ```python
    # ---- Core Processing Logic ----
    # File: aicoder/core/processor.py

    import shutil
    import subprocess
    import time
    from pathlib import Path

    from ..llm.api_client import LLMClient
    from ..llm.prompts import DocumentationPrompts, TwigDocumentationPrompts
    from ..strategies import UDiffStrategy, ChangeStrategy
    from ..utils.logger import myLogger


    def _validate_code(pathOriginalFile: Path, pathModifiedCodeTempFile: Path) -> bool:
        """Dispatcher to select the correct validation script based on file extension."""
        file_extension = pathOriginalFile.suffix.lower()
        
        if file_extension == '.php':
            validator_script = Path(__file__).parent.parent.parent / 'compare-php-files' / 'compare-php-files.php'
            script_name = "PHP"
        elif file_extension == '.twig':
            validator_script = Path(__file__).parent.parent.parent / 'compare-twig-files' / 'compare-twig-files.php'
            script_name = "Twig"
        else:
            myLogger.error(f"No validator found for file type: {file_extension}")
            return False

        if not validator_script.exists():
            raise RuntimeError(f"{script_name} comparison script not found at {validator_script}")

        try:
            myLogger.info(f"Validating {script_name} code changes...")
            cmd = ['php', str(validator_script), str(pathOriginalFile), str(pathModifiedCodeTempFile)]
            myLogger.debug(f"Running command: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode != 0:
                myLogger.error(f"Error running {script_name} comparison script: {result.stderr}")
                return False
                
            is_valid = result.stdout.strip() == 'true'
            
            if is_valid:
                myLogger.success(f"{script_name} code validation passed")
                return True
            else:
                myLogger.error(f"{script_name} code validation failed - functionality changed")
                # Show colored diff
                diff_result = subprocess.run(
                    ['diff', '--color=always', str(pathOriginalFile), str(pathModifiedCodeTempFile)],
                    capture_output=True,
                    text=True
                )
                if diff_result.stdout or diff_result.stderr:
                    myLogger.warning("Differences found:")
                    print(diff_result.stdout or diff_result.stderr)
                return False
        except Exception as e:
            myLogger.error(f"An unexpected error occurred during {script_name} validation: {str(e)}")
            return False


    def improve_file_documentation(pathOrigFile: Path,
                                  model: str,
                                  strategy: ChangeStrategy) -> None:
        """Process a file through the documentation pipeline, detecting its type."""
        originalCode = pathOrigFile.read_text()
        file_extension = pathOrigFile.suffix.lower()

        if file_extension == '.php':
            prompt_provider = DocumentationPrompts
        elif file_extension == '.twig':
            prompt_provider = TwigDocumentationPrompts
        else:
            raise ValueError(f"Unsupported file type: '{file_extension}'. Only .php and .twig files are supported.")

        try:
            start_time = time.time()
            
            num_rows = originalCode.count('\n') + 1
            myLogger.info(f"⏳ Analyzing [magenta]{pathOrigFile.name}[/magenta]: {len(originalCode):,} characters / {num_rows:,} lines...")
            
            systemPrompt, userPrompt = prompt_provider.get_full_prompt(originalCode, strategy)
            llmResponseRaw = LLMClient(modelWithPrefix=model).sendRequest(systemPrompt, userPrompt)
            myLogger.success(f"LLM request completed in {time.time() - start_time:.1f}s")
            myLogger.debug(f"[blue]Raw Response from LLM {model}[/blue]\n")
            myLogger.debug(f"{llmResponseRaw}", highlight=False)

            pathModifiedCodeTempFile = strategy.process_llm_response(llmResponseRaw, pathOrigFile)
            if pathModifiedCodeTempFile is None:
                myLogger.warning("No changes were made to the file")
                return

            myLogger.success(f"Temp file {pathModifiedCodeTempFile} was created.")
            
            is_valid = _validate_code(pathOrigFile, pathModifiedCodeTempFile)
            if not is_valid:
                raise RuntimeError(
                    f"Failed to process {pathOrigFile.name}: Code validation failed. "
                    "The changes would alter the code functionality."
                )

            if pathModifiedCodeTempFile and pathModifiedCodeTempFile.exists():
                diff_result = subprocess.run(
                    ['diff', '-u', '--color=always', str(pathOrigFile), str(pathModifiedCodeTempFile)],
                    capture_output=True,
                    text=True
                )
                if diff_result.stdout or diff_result.stderr:
                    myLogger.success("Applied changes:")
                    print(diff_result.stdout or diff_result.stderr)
                    shutil.copystat(pathOrigFile, pathModifiedCodeTempFile)
                    shutil.copy2(pathModifiedCodeTempFile, pathOrigFile)
                else:
                    myLogger.warning("No changes were made to the file")
                
                pathModifiedCodeTempFile.unlink()
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
    ```

---

### Phase 3: Update the CLI Command and User Interface

This phase updates the user-facing part of the tool to reflect the new capabilities.

1.  **Update the `add-comments` Command**
    Modify `aicoder/cli/commands/add_comments.py` to accept `.twig` files and to call the newly renamed processor function. Also, add a clear log message indicating which file is being processed.

    **File:** `aicoder/cli/commands/add_comments.py`
    ```python
    import typer
    from pathlib import Path
    from typing import Optional

    from aicoder.config import Config
    from aicoder.profiles import profile_loader, ProfileType
    from aicoder.strategies import UDiffStrategy, WholeFileStrategy, SearchReplaceStrategy
    from aicoder.core.processor import improve_file_documentation  # <--- UPDATED IMPORT
    from aicoder.utils.error_handler import handle_error
    from aicoder.utils.output import print_success
    from aicoder.utils.logger import myLogger

    def add_comments_command(
        profile: str = typer.Option(
            Config.DEFAULT_PROFILE, "--profile", "-p",
            help="Profile to use (predefined model and strategy combination)",
            show_default=True
        ),
        model: Optional[str] = typer.Option(
            None, "--model",
            help="Model to use for processing (overrides profile setting)",
            show_default=False
        ),
        strategy: Optional[str] = typer.Option(
            None, "--strategy",
            help="Strategy for output format: wholefile, udiff, or searchreplace (overrides profile setting)",
            show_default=False
        ),
        verbose: bool = typer.Option(
            False, "--verbose", "-v",
            help="Enable verbose output"
        ),
        file_path: Path = typer.Argument(..., help="Path to PHP or Twig file to document", exists=True) # <--- UPDATED HELP TEXT
    ):
        """
        Add PHPDoc comments to a PHP file or explanatory comments to a Twig file.
        
        Features:
        - Generates PHPDoc blocks for PHP classes and functions.
        - Adds explanatory comments for Twig templates.
        - Preserves original code structure and functionality.
        """
        try:
            myLogger.set_verbose(verbose)
            myLogger.info(f"Processing file {file_path.resolve()}...") # <--- ADDED INFO MESSAGE

            profile_settings = profile_loader.get_profile(ProfileType.COMMENTER, profile)
            if not profile_settings:
                available_profiles = [
                    f"- {name} (model: {details['model']}, strategy: {details['strategy']})"
                    for name, details in profile_loader.profiles[ProfileType.COMMENTER].items()
                ]
                raise ValueError(
                    f"Profile '{profile}' not found. Available profiles:\n" +
                    "\n".join(available_profiles)
                )
            
            selected_model = model or profile_settings["model"]
            selected_strategy = strategy or profile_settings["strategy"]
            
            myLogger.debug(f"Using profile: {profile}")
            myLogger.debug(f"Model: {selected_model}")
            myLogger.debug(f"Strategy: {selected_strategy}")
            
            if selected_strategy.lower() == "searchreplace":
                strategy_obj = SearchReplaceStrategy()
            elif selected_strategy.lower() == "udiff":
                strategy_obj = UDiffStrategy()
            elif selected_strategy.lower() == "wholefile":
                strategy_obj = WholeFileStrategy()
            else:
                raise ValueError(f"Invalid strategy: {selected_strategy}. Choose from: wholefile, udiff, searchreplace")
            
            myLogger.debug(f"Using strategy: {strategy_obj.__class__.__name__}")
            myLogger.info(f"Sending request to LLM {selected_model}...")
            
            improve_file_documentation(file_path, model=selected_model, strategy=strategy_obj) # <--- UPDATED FUNCTION CALL
            print_success(f"\n✅ Successfully updated documentation in [bold]{file_path}[/bold]")
                
        except Exception as e:
            handle_error(e)
    ```

---

### Phase 4: Verification

This final phase ensures the new functionality works correctly.

1.  **Create a Test Twig File**
    Create a new file named `test.twig` in the project root for testing purposes.

    **File:** `test.twig`
    ```twig
    {% set name = "World" %}

    <div>
        {% if name %}
            <h1>Hello {{ name }}!</h1>
        {% else %}
            <h1>Hello Stranger!</h1>
        {% endif %}
    </div>
    ```

2.  **Run the `add-comments` Command**
    Execute the tool on the new Twig file using your preferred profile.

    ```bash
    aicoder add-comments --profile default test.twig
    ```

3.  **Verify the Output**
    Confirm that the command executes without errors. The output should show:
    - The "Processing file..." message.
    - The "Analyzing..." message.
    - The "Validating Twig code changes..." message.
    - The "Twig code validation passed" success message.
    - A diff showing the addition of `{# ... #}` comments to the `test.twig` file.
    - The final success message.

4.  **Clean Up**
    Remove the `test.twig` file after verification.

