"""Test cases for document processor."""
import pytest
import shutil
from pathlib import Path
from docx import Document
from src.processor import DocumentProcessor


@pytest.fixture(autouse=True)
def clean_output_directory(output_dir):
    """Clean output directory before and after each test."""
    # Clean before test
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Run test
    yield

    # Clean after test
    if output_dir.exists():
        shutil.rmtree(output_dir)


def test_document_processor_initialization(test_config):
    """Test processor initialization."""
    processor = DocumentProcessor(test_config, dry_run=False)
    assert processor.pattern_type == "plain"
    assert len(processor.rules) == 1
    assert processor.rules[0]["old_text"] == "公司A"


def test_document_processing(test_config, sample_docx, output_dir):
    """Test document processing with actual file."""
    # Process the document
    processor = DocumentProcessor(test_config, dry_run=False)
    processor.process_document(sample_docx, output_dir)

    # Check the output file
    output_file = output_dir / sample_docx.name
    assert output_file.exists()

    # Verify content changes
    doc = Document(str(output_file))
    first_paragraph = doc.paragraphs[0].text
    assert "DeepSeek" in first_paragraph, f"Expected 'DeepSeek' in '{first_paragraph}'"
    assert "公司A" not in first_paragraph, f"Found unexpected '公司A' in '{first_paragraph}'"


def test_dry_run_mode(test_config, sample_docx, output_dir):
    """Test dry run mode."""
    processor = DocumentProcessor(test_config, dry_run=True)
    processor.process_document(sample_docx, output_dir)

    # Check that no output file was created
    output_file = output_dir / sample_docx.name
    assert not output_file.exists(), "Output file should not exist in dry run mode"
