import os
import pytest
from app.utils import read_local_file, extract_pdf_to_txt


def test_read_local_file(tmp_path):
    test_file = tmp_path / "test.txt"
    test_content = "Hello, this is a test."
    test_file.write_text(test_content)
    result = read_local_file(str(test_file))
    assert result == test_content


def test_read_local_file_file_not_found():
    with pytest.raises(FileNotFoundError):
        read_local_file("nonexistent_file.txt")


# 🧪 Fixture to get the PDF file path from env
@pytest.fixture
def sample_pdf_path():
    path = os.environ.get("PYTEST_PDF")
    if not path or not os.path.exists(path):
        pytest.skip("PDF test file not available or path invalid.")
    return path


@pytest.mark.skipif("PYTEST_PDF" not in os.environ, reason="PDF testing not enabled")
def test_extract_pdf_to_text(sample_pdf_path):
    result = extract_pdf_to_txt(sample_pdf_path)
    assert isinstance(result, str)
    assert len(result) > 0
