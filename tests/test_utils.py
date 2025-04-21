import os
import pytest
from app.utils import read_local_file, extract_pdf_to_txt


def test_read_local_file(tmp_path):
    # Arrange
    test_file = tmp_path / "test.txt"
    test_content = "Hello, this is a test."
    test_file.write_text(test_content)

    # Act
    result = read_local_file(str(test_file))

    # Assert
    assert result == test_content


def test_read_local_file_file_not_found():
    with pytest.raises(FileNotFoundError):
        read_local_file("nonexistent_file.txt")


@pytest.mark.skipif("PYTEST_PDF" not in os.environ, reason="PDF testing not enabled")
def test_extract_pdf_to_text(sample_pdf_path):
    # Assuming sample_pdf_path is a fixture providing a sample .pdf file
    result = extract_pdf_to_text(sample_pdf_path)
    assert isinstance(result, str)
    assert "expected text" in result  # Adjust based on your actual test file


# Optional fixture
@pytest.fixture
def sample_pdf_path(tmp_path):
    import io
    from reportlab.pdfgen import canvas

    file_path = tmp_path / "sample.pdf"
    c = canvas.Canvas(str(file_path))
    c.drawString(100, 750, "expected text")
    c.save()

    return str(file_path)
