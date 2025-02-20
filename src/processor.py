"""Document processing functionality."""
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, Any, List, Tuple
import re
from docx import Document
from docx.text.paragraph import Paragraph
from docx.text.run import Run

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

    def process_document(self, file_path: Path, output_path: Path) -> None:
        """Process a single document."""
        logger.info(f"Processing document: {file_path}")

        if self.dry_run:
            logger.info(f"Dry run - would process {file_path}")
            self._preview_changes(file_path)
            return

        try:
            doc = Document(str(file_path))  # Convert Path to string
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
                doc.save(str(output_file))  # Convert Path to string
                logger.info(f"Saved modified document to {output_file}")
            else:
                logger.info(f"No changes needed for {file_path}")

        except Exception as e:
            logger.error(f"Error processing {file_path}: {str(e)}")
            raise

    def _process_paragraph(self, paragraph: Paragraph) -> bool:
        """Process a single paragraph, returns True if any changes were made."""
        if not paragraph.text:
            return False

        modified = False
        for rule in self.rules:
            old_text = rule["old_text"]
            new_text = rule["new_text"]
            options = rule.get("options", {})

            # Simple text replacement for now
            if old_text in paragraph.text:
                # Clear the paragraph
                p_text = paragraph.text
                for run in paragraph.runs:
                    run.text = ""

                # Replace text
                new_p_text = p_text.replace(old_text, new_text)

                # Add back the text in a single run
                run = paragraph.add_run(new_p_text)

                # Apply formatting if needed
                if options.get("preserve_format", True):
                    # Apply some basic formatting (expand as needed)
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
                logger.info(f"\nPreview of changes for {file_path}:")
                for i, change in enumerate(changes, 1):
                    logger.info(f"\nChange {i}:")
                    logger.info(f"Old text: {change['old_text']}")
                    logger.info(f"New text: {change['new_text']}")
                    logger.info(f"Context: {change['context']}")
            else:
                logger.info(f"No changes would be made to {file_path}")

        except Exception as e:
            logger.error(f"Error previewing changes for {file_path}: {str(e)}")
