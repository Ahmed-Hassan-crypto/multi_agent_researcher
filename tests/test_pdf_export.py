import unittest
import os
import tempfile
from unittest.mock import Mock, patch
from datetime import datetime

from utils.pdf_export import generate_pdf, PDF, sanitize_text


class TestSanitizeText(unittest.TestCase):
    """Tests for text sanitization function."""

    def test_sanitize_replaces_curly_quotes(self):
        """Test curly quotes are replaced with straight quotes."""
        text = 'He said "Hello" and "Goodbye"'
        result = sanitize_text(text)
        self.assertEqual(result, 'He said "Hello" and "Goodbye"')

    def test_sanitize_replaces_em_dashes(self):
        """Test em dashes are replaced with hyphens."""
        text = "Hello — world"
        result = sanitize_text(text)
        self.assertEqual(result, "Hello - world")

    def test_sanitize_replaces_en_dashes(self):
        """Test en dashes are replaced with hyphens."""
        text = "Hello – world"
        result = sanitize_text(text)
        self.assertEqual(result, "Hello - world")

    def test_sanitize_replaces_bullets(self):
        """Test bullet points are replaced with hyphens."""
        text = "• Item 1\n• Item 2"
        result = sanitize_text(text)
        self.assertEqual(result, "- Item 1\n- Item 2")

    def test_sanitize_handles_unicode(self):
        """Test unicode characters are handled."""
        text = "Café résumé"
        result = sanitize_text(text)
        self.assertIn("Caf", result)

    def test_sanitize_empty_string(self):
        """Test empty string handling."""
        result = sanitize_text("")
        self.assertEqual(result, "")


class TestPDFGeneration(unittest.TestCase):
    """Tests for PDF generation function."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up temporary files."""
        for file in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, file))
        os.rmdir(self.temp_dir)

    def test_generate_pdf_creates_file(self):
        """Test PDF file is created."""
        output_path = os.path.join(self.temp_dir, "test_report.pdf")
        result = generate_pdf(
            topic="Test Topic",
            markdown_content="# Test Report\n\nThis is a test.",
            search_results=[{"title": "Source 1", "url": "http://example.com"}],
            output_filename=output_path,
        )
        self.assertTrue(os.path.exists(result))

    def test_generate_pdf_contains_topic(self):
        """Test PDF contains the topic in title."""
        output_path = os.path.join(self.temp_dir, "topic_test.pdf")
        generate_pdf(
            topic="Machine Learning",
            markdown_content="# ML Report",
            search_results=[],
            output_filename=output_path,
        )
        with open(output_path, "rb") as f:
            content = f.read()
        self.assertIn(b"Machine Learning", content)

    def test_generate_pdf_contains_date(self):
        """Test PDF contains generation date."""
        output_path = os.path.join(self.temp_dir, "date_test.pdf")
        generate_pdf(
            topic="Test",
            markdown_content="Content",
            search_results=[],
            output_filename=output_path,
        )
        with open(output_path, "rb") as f:
            content = f.read()
        current_date = datetime.now().strftime("%B %d, %Y")
        self.assertIn(current_date.encode(), content)

    def test_generate_pdf_includes_references(self):
        """Test PDF includes references section."""
        output_path = os.path.join(self.temp_dir, "refs_test.pdf")
        generate_pdf(
            topic="Test",
            markdown_content="# Report",
            search_results=[
                {"title": "Article 1", "url": "http://article1.com"},
                {"title": "Article 2", "url": "http://article2.com"},
            ],
            output_filename=output_path,
        )
        with open(output_path, "rb") as f:
            content = f.read()
        self.assertIn(b"References", content)
        self.assertIn(b"article1.com", content)

    def test_generate_pdf_empty_content(self):
        """Test PDF generation with empty content."""
        output_path = os.path.join(self.temp_dir, "empty_test.pdf")
        result = generate_pdf(
            topic="Empty",
            markdown_content="",
            search_results=[],
            output_filename=output_path,
        )
        self.assertTrue(os.path.exists(result))

    def test_generate_pdf_with_markdown(self):
        """Test PDF handles markdown formatting."""
        output_path = os.path.join(self.temp_dir, "markdown_test.pdf")
        markdown = """# Heading 1

## Heading 2

**Bold text** and *italic text*

- List item 1
- List item 2
"""
        generate_pdf(
            topic="Markdown Test",
            markdown_content=markdown,
            search_results=[],
            output_filename=output_path,
        )
        self.assertTrue(os.path.exists(output_path))


class TestPDFClass(unittest.TestCase):
    """Tests for PDF class."""

    def test_pdf_initialization(self):
        """Test PDF class can be initialized."""
        pdf = PDF()
        self.assertEqual(pdf.page, 0)

    def test_pdf_header_method_exists(self):
        """Test PDF has header method."""
        pdf = PDF()
        self.assertTrue(hasattr(pdf, "header"))
        self.assertTrue(callable(getattr(pdf, "header")))

    def test_pdf_footer_method_exists(self):
        """Test PDF has footer method."""
        pdf = PDF()
        self.assertTrue(hasattr(pdf, "footer"))
        self.assertTrue(callable(getattr(pdf, "footer")))


if __name__ == "__main__":
    unittest.main()
