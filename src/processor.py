"""Document processing functionality."""
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import re
from docx import Document
from docx.text.paragraph import Paragraph
from docx.text.run import Run
from docx.oxml.text.run import CT_R
from docx.shared import RGBColor

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Handles the processing of Word documents."""

    def __init__(self, config: Dict[str, Any], dry_run: bool = False):
        """Initialize the document processor."""
        self.config = config
        self.dry_run = dry_run
        self.replacements = config["replacements"]
        self.file_settings = config["file_settings"]
        self.advanced = config["advanced"]
        self.pattern_type = self.replacements["pattern_type"]
        self.rules = self.replacements["rules"]

        # Compile regex patterns if using regex mode
        if self.pattern_type == "regex":
            for rule in self.rules:
                rule["pattern"] = re.compile(rule["old_text"])

    def process_all(self) -> None:
        """Process all documents in the input directory."""
        input_path = Path(self.file_settings["input_path"])
        output_path = Path(self.file_settings["output_path"])

        if not input_path.exists():
            raise FileNotFoundError(f"Input path does not exist: {input_path}")

        # Ensure output directory exists
        output_path.mkdir(parents=True, exist_ok=True)

        files_to_process = self._get_files_to_process(input_path)
        if not files_to_process:
            logger.warning("No files found to process")
            return

        with ThreadPoolExecutor(max_workers=self.advanced["max_workers"]) as executor:
            future_to_file = {
                executor.submit(self.process_document, file_path, output_path): file_path
                for file_path in files_to_process
            }

            for future in as_completed(future_to_file):
                file_path = future_to_file[future]
                try:
                    future.result(timeout=self.advanced["timeout"])
                except Exception as e:
                    logger.error(f"Error processing {file_path}: {str(e)}")

    def _get_files_to_process(self, input_path: Path) -> List[Path]:
        """Get list of files to process."""
        files = []
        for file_type in self.file_settings["file_types"]:
            files.extend(input_path.glob(f"**/*{file_type}"))
        return files

    def process_document(self, file_path: Path, output_path: Path) -> None:
        """Process a single document."""
        logger.info(f"Processing document: {file_path}")

        if self.dry_run:
            logger.info(f"Dry run - would process {file_path}")
            self._preview_changes(file_path)
            return

        try:
            doc = Document(file_path)
            modified = False

            # Process each paragraph in the document
            for paragraph in doc.paragraphs:
                if self._process_paragraph(paragraph):
                    modified = True

            # Process tables
            for table in doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        for paragraph in cell.paragraphs:
                            if self._process_paragraph(paragraph):
                                modified = True

            if modified:
                output_file = output_path / file_path.name
                doc.save(output_file)
                logger.info(f"Saved modified document to {output_file}")
            else:
                logger.info(f"No changes needed for {file_path}")

        except Exception as e:
            logger.error(f"Error processing {file_path}: {str(e)}")
            raise

    def _process_paragraph(self, paragraph: Paragraph) -> bool:
        """Process a single paragraph, returns True if any changes were made."""
        modified = False

        # Get the initial text content
        original_text = paragraph.text

        # Process each rule
        for rule in self.rules:
            options = rule.get("options", {})
            case_sensitive = options.get("case_sensitive", True)
            whole_word = options.get("whole_word", True)
            preserve_format = options.get("preserve_format", True)

            # Find all matches and their runs
            matches = self._find_matches(
                paragraph, rule, case_sensitive, whole_word)

            for match_text, runs in matches:
                if self._replace_text_in_runs(runs, match_text, rule["new_text"], preserve_format):
                    modified = True

        return modified

    def _find_matches(self, paragraph: Paragraph, rule: Dict[str, Any],
                      case_sensitive: bool, whole_word: bool) -> List[Tuple[str, List[Run]]]:
        """Find all matches in a paragraph and their corresponding runs."""
        matches = []
        text = paragraph.text

        if self.pattern_type == "regex":
            pattern = rule["pattern"]
            if not case_sensitive:
                pattern = re.compile(pattern.pattern, re.IGNORECASE)
        else:
            old_text = rule["old_text"]
            if whole_word:
                pattern = re.compile(r'\b' + re.escape(old_text) + r'\b',
                                     re.IGNORECASE if not case_sensitive else 0)
            else:
                pattern = re.compile(re.escape(old_text),
                                     re.IGNORECASE if not case_sensitive else 0)

        for match in pattern.finditer(text):
            start, end = match.span()
            match_text = match.group()
            runs = self._get_runs_for_range(paragraph, start, end)
            if runs:
                matches.append((match_text, runs))

        return matches

    def _get_runs_for_range(self, paragraph: Paragraph, start: int, end: int) -> List[Run]:
        """Get all runs that contain text within the given range."""
        runs = []
        current_pos = 0

        for run in paragraph.runs:
            run_length = len(run.text)
            run_end = current_pos + run_length

            # Check if this run overlaps with the target range
            if current_pos < end and run_end > start:
                runs.append(run)

            current_pos = run_end

            if current_pos >= end:
                break

        return runs

    def _replace_text_in_runs(self, runs: List[Run], old_text: str,
                              new_text: str, preserve_format: bool) -> bool:
        """Replace text in runs while preserving formatting."""
        if not runs:
            return False

        # If only one run contains the text, simple replacement
        if len(runs) == 1:
            run = runs[0]
            run.text = run.text.replace(old_text, new_text)
            return True

        # For multiple runs, we need to handle the replacement carefully
        total_text = "".join(run.text for run in runs)
        replacement_length = len(new_text)

        # Split the new text proportionally among runs
        start_pos = 0
        for run in runs:
            run_length = len(run.text)
            proportion = run_length / len(total_text)
            chars_to_replace = int(replacement_length * proportion)

            if preserve_format:
                # Preserve original formatting by copying formatting from the first run
                run.font.name = runs[0].font.name
                run.font.size = runs[0].font.size
                run.font.bold = runs[0].font.bold
                run.font.italic = runs[0].font.italic

            if start_pos >= len(new_text):
                run.text = ""
            else:
                end_pos = min(start_pos + chars_to_replace, len(new_text))
                run.text = new_text[start_pos:end_pos]
                start_pos = end_pos

        return True

    def _preview_changes(self, file_path: Path) -> None:
        """Preview changes that would be made to the document."""
        try:
            doc = Document(file_path)
            changes = []

            for paragraph in doc.paragraphs:
                original_text = paragraph.text
                for rule in self.rules:
                    options = rule.get("options", {})
                    case_sensitive = options.get("case_sensitive", True)
                    whole_word = options.get("whole_word", True)

                    if self.pattern_type == "regex":
                        pattern = rule["pattern"]
                        if not case_sensitive:
                            pattern = re.compile(
                                pattern.pattern, re.IGNORECASE)
                        matches = pattern.finditer(original_text)
                    else:
                        old_text = rule["old_text"]
                        if whole_word:
                            pattern = re.compile(r'\b' + re.escape(old_text) + r'\b',
                                                 re.IGNORECASE if not case_sensitive else 0)
                        else:
                            pattern = re.compile(re.escape(old_text),
                                                 re.IGNORECASE if not case_sensitive else 0)
                        matches = pattern.finditer(original_text)

                    for match in matches:
                        changes.append({
                            "old_text": match.group(),
                            "new_text": rule["new_text"],
                            "context": original_text[max(0, match.start()-30):
                                                     min(len(original_text), match.end()+30)]
                        })

            if changes:
                logger.info(f"\nPreview of changes for {file_path}:")
                for i, change in enumerate(changes, 1):
                    logger.info(f"\nChange {i}:")
                    logger.info(f"Old text: {change['old_text']}")
                    logger.info(f"New text: {change['new_text']}")
                    logger.info(f"Context: ...{change['context']}...")
            else:
                logger.info(f"No changes would be made to {file_path}")

        except Exception as e:
            logger.error(f"Error previewing changes for {file_path}: {str(e)}")
