"""Document processing functionality."""
from src.logger_config import setup_logger
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, Any, List
from docx.text.paragraph import Paragraph
from docx import Document


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

        # Set the log level from config if available, otherwise default remains
        self.logger = setup_logger(
            "src.processor", level=config.get("log_level", "debug"))

    def _get_files_to_process(self, input_path: Path) -> List[Path]:
        """Get list of files to process based on configured file types."""
        files = []
        for file_type in self.file_settings["file_types"]:
            if not file_type.startswith('.'):
                file_type = f'.{file_type}'
            files.extend(input_path.rglob(f'*{file_type}'))

        self.logger.info(
            f"Found {len(files)} files to process in {input_path}")
        for file in files:
            self.logger.debug(f"Found file: {file}")
        return files

    def process_all(self) -> None:
        """Process all documents in the input directory."""
        input_path = Path(self.file_settings["input_path"])
        output_path = Path(self.file_settings["output_path"])

        if not input_path.exists():
            raise FileNotFoundError(f"Input path does not exist: {input_path}")

        if not self.dry_run:
            output_path.mkdir(parents=True, exist_ok=True)

        files_to_process = self._get_files_to_process(input_path)
        if not files_to_process:
            self.logger.warning("No files found to process")
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
                    self.logger.error(
                        f"Error processing {file_path}: {str(e)}")

    def process_document(self, file_path: Path, output_path: Path) -> None:
        """Process a single document."""
        self.logger.info(f"Processing document: {file_path}")

        if self.dry_run:
            self.logger.info(f"Dry run - would process {file_path}")
            self._preview_changes(file_path)
            return

        try:
            doc = Document(str(file_path))
            modified = False

            for paragraph in doc.paragraphs:
                if self._process_paragraph(paragraph):
                    modified = True

            for table in doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        for paragraph in cell.paragraphs:
                            if self._process_paragraph(paragraph):
                                modified = True

            if modified and not self.dry_run:
                output_file = output_path / file_path.name
                doc.save(str(output_file))
                self.logger.info(f"Saved modified document to {output_file}")
            else:
                self.logger.info(f"No changes needed for {file_path}")

        except Exception as e:
            self.logger.error(f"Error processing {file_path}: {str(e)}")
            raise

    def _process_paragraph(self, paragraph: Paragraph) -> bool:
        """Process a single paragraph; returns True if any changes were made."""
        if not paragraph.text:
            return False

        modified = False
        for rule in self.rules:
            old_text = rule["old_text"]
            new_text = rule["new_text"]

            if old_text in paragraph.text:
                p_text = paragraph.text
                if not self.dry_run:
                    for run in paragraph.runs:
                        run.text = ""
                    new_p_text = p_text.replace(old_text, new_text)
                    run = paragraph.add_run(new_p_text)
                    run.bold = True
                modified = True
        return modified

    def _preview_changes(self, file_path: Path) -> None:
        """Preview changes that would be made to the document."""
        try:
            doc = Document(str(file_path))
            changes = []

            for paragraph in doc.paragraphs:
                if not paragraph.text:
                    continue

                original_text = paragraph.text
                for rule in self.rules:
                    old_text = rule["old_text"]
                    new_text = rule["new_text"]

                    if old_text in original_text:
                        changes.append({
                            "old_text": old_text,
                            "new_text": new_text,
                            "context": original_text
                        })

            if changes:
                self.logger.info(f"\nPreview of changes for {file_path}:")
                for i, change in enumerate(changes, 1):
                    self.logger.info(f"\nChange {i}:")
                    self.logger.info(f"Old text: {change['old_text']}")
                    self.logger.info(f"New text: {change['new_text']}")
                    self.logger.info(f"Context: {change['context']}")
            else:
                self.logger.info(f"No changes would be made to {file_path}")

        except Exception as e:
            self.logger.error(
                f"Error previewing changes for {file_path}: {str(e)}")
            raise
