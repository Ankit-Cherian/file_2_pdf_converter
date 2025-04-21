# test_app.py - Tests for File2PDF conversion functionality
# Run with: pytest -v test_app.py

import os
import pytest
from unittest.mock import MagicMock, patch
import sys
import importlib
import subprocess

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.app import ConversionWorker

# First 5 tests remain unchanged
# Test conversion worker
def test_conversion_worker():
    """Test basic worker functionality."""
    worker = ConversionWorker("input.txt", "output.pdf")
    assert worker.file_path == "input.txt"
    assert worker.output_path == "output.pdf"
    
    # Test signals with mocks
    progress_mock = MagicMock()
    complete_mock = MagicMock()
    
    worker.update_progress.connect(progress_mock)
    worker.conversion_complete.connect(complete_mock)
    
    # Run with patched time.sleep to avoid delays
    with patch('time.sleep'):
        worker.run()
    
    # Verify progress updates and completion signal
    assert progress_mock.call_count > 0
    complete_mock.assert_called_once()

# Test image conversion worker
def test_image_conversion_worker():
    """Test image conversion worker functionality."""
    # Create a worker with an image file
    worker = ConversionWorker("input.jpg", "output.pdf")
    assert worker.file_path == "input.jpg"
    assert worker.output_path == "output.pdf"
    
    # Test signals with mocks
    progress_mock = MagicMock()
    complete_mock = MagicMock()
    
    worker.update_progress.connect(progress_mock)
    worker.conversion_complete.connect(complete_mock)
    
    # Mock the image conversion method to avoid actual conversion
    with patch.object(worker, 'convert_image_to_pdf') as mock_convert:
        with patch('time.sleep'):
            worker.run()
        
        # Verify the image conversion method was called
        mock_convert.assert_called_once()
    
    # Verify signal was emitted
    complete_mock.assert_called_once()

# Test image conversion method
def test_convert_image_to_pdf():
    """Test the image to PDF conversion method."""
    worker = ConversionWorker("input.jpg", "output.pdf")
    
    # Mock required library imports
    with patch('PIL.Image.open') as mock_open:
        # Set up the mock image
        mock_img = MagicMock()
        mock_img.size = (100, 100)
        mock_open.return_value = mock_img
        
        # Mock canvas
        mock_canvas = MagicMock()
        with patch('reportlab.pdfgen.canvas.Canvas') as mock_canvas_class:
            mock_canvas_class.return_value = mock_canvas
            
            # Test the conversion method
            with patch('time.sleep'):
                worker.convert_image_to_pdf()
            
            # Verify canvas was created and methods were called
            mock_canvas_class.assert_called_once_with("output.pdf", pagesize=(100, 100))
            mock_canvas.drawImage.assert_called_once_with("input.jpg", 0, 0, 100, 100)
            mock_canvas.save.assert_called_once()

# Test image conversion error
def test_image_conversion_error():
    """Test error handling in the image conversion process."""
    worker = ConversionWorker("input.jpg", "output.pdf")
    
    # Mock PIL import to raise an exception
    with patch('PIL.Image.open', side_effect=Exception("Image conversion error")):
        # Test that exception is properly handled
        with pytest.raises(Exception) as excinfo:
            worker.convert_image_to_pdf()
        
        # Verify error message
        assert "Image conversion failed" in str(excinfo.value)
        assert "Image conversion error" in str(excinfo.value)

# Test text conversion method
def test_convert_text_to_pdf():
    """Test the text to PDF conversion method."""
    worker = ConversionWorker("input.txt", "output.pdf")
    
    # Mock file reading
    mock_file_content = ["Line 1\n", "Line 2\n", "Line 3\n"]
    mock_file = MagicMock()
    mock_file.__enter__.return_value.readlines.return_value = mock_file_content
    
    with patch('builtins.open', return_value=mock_file):
        # Mock canvas
        mock_canvas = MagicMock()
        with patch('reportlab.pdfgen.canvas.Canvas') as mock_canvas_class:
            mock_canvas_class.return_value = mock_canvas
            # Mock font registration
            with patch('reportlab.pdfbase.pdfmetrics.registerFont'):
                # Test the conversion method
                worker.convert_text_to_pdf()
            
            # Verify canvas was created
            mock_canvas_class.assert_called_once()
            # Verify save was called
            mock_canvas.save.assert_called_once()

# Test HTML conversion worker
def test_html_conversion_worker():
    """Test HTML conversion worker functionality."""
    # Create a worker with an HTML file
    worker = ConversionWorker("input.html", "output.pdf")
    assert worker.file_path == "input.html"
    assert worker.output_path == "output.pdf"
    
    # Test signals with mocks
    progress_mock = MagicMock()
    complete_mock = MagicMock()
    
    worker.update_progress.connect(progress_mock)
    worker.conversion_complete.connect(complete_mock)
    
    # Mock the HTML conversion method to avoid actual conversion
    with patch.object(worker, 'convert_html_to_pdf') as mock_convert:
        with patch('time.sleep'):
            worker.run()
        
        # Verify the HTML conversion method was called
        mock_convert.assert_called_once()
    
    # Verify signal was emitted
    complete_mock.assert_called_once()

# NEW FIXED HTML CONVERSION TESTS

# Test HTML conversion method with success path
def test_convert_html_to_pdf():
    """Test the HTML to PDF conversion method."""
    worker = ConversionWorker("input.html", "output.pdf")
    
    # Mock file reading
    mock_file_content = "<html><body><h1>Test</h1></body></html>"
    mock_file = MagicMock()
    mock_file.__enter__.return_value.read.return_value = mock_file_content
    
    # Create a mock weasyprint module
    mock_wp_html = MagicMock()
    mock_wp_html.return_value.write_pdf = MagicMock()
    
    # Setup the mocks properly - this is the key fix
    with patch.dict('sys.modules', {'weasyprint': MagicMock(HTML=mock_wp_html)}):
        with patch('builtins.open', return_value=mock_file):
            # Test the conversion method
            worker.convert_html_to_pdf()
            
            # Verify the HTML conversion worked correctly
            mock_wp_html.assert_called_once_with(string=mock_file_content)
            mock_wp_html.return_value.write_pdf.assert_called_once_with(worker.output_path)

# Test HTML conversion fallback for ImportError
def test_html_conversion_fallback():
    """Test HTML conversion fallback to text conversion when WeasyPrint is not available."""
    worker = ConversionWorker("input.html", "output.pdf")
    
    # Mock file reading
    mock_file = MagicMock()
    
    # Mock text conversion
    with patch.object(worker, 'convert_text_to_pdf') as mock_text_convert:
        # Mock the import mechanism to raise ImportError
        with patch('builtins.__import__', side_effect=lambda name, *args, **kwargs:
                  raise_(ImportError("No module named 'weasyprint'")) if name == 'weasyprint' else 
                  importlib.__import__(name, *args, **kwargs)):
            with patch('builtins.open', return_value=mock_file):
                # Test the conversion method
                worker.convert_html_to_pdf()
            
            # Verify fallback to text conversion
            mock_text_convert.assert_called_once()

# Helper function for raising exceptions in lambda
def raise_(ex):
    raise ex

# Test HTML conversion fallback for OSError
def test_html_conversion_oserror_fallback():
    """Test HTML conversion fallback when WeasyPrint dependencies are missing."""
    worker = ConversionWorker("input.html", "output.pdf")
    
    # Mock file reading
    mock_file = MagicMock()
    
    # Setup the mock for text conversion
    with patch.object(worker, 'convert_text_to_pdf') as mock_text_convert:
        # Setup a partial mock that simulates OSError during weasyprint import
        mock_wp = MagicMock()
        mock_wp.HTML = MagicMock(side_effect=OSError("Cannot load library"))
        
        with patch.dict('sys.modules', {'weasyprint': mock_wp}):
            with patch('builtins.open', return_value=mock_file):
                # Test the conversion method
                worker.convert_html_to_pdf()
            
            # Verify fallback to text conversion
            mock_text_convert.assert_called_once()

# Test HTML conversion error
def test_html_conversion_error():
    """Test error handling in the HTML conversion process."""
    worker = ConversionWorker("input.html", "output.pdf")
    
    # Mock file reading to raise an exception
    with patch('builtins.open', side_effect=Exception("HTML conversion error")):
        # Test that exception is properly handled
        with pytest.raises(Exception) as excinfo:
            worker.convert_html_to_pdf()
        
        # Verify error message
        assert "HTML conversion failed" in str(excinfo.value)
        assert "HTML conversion error" in str(excinfo.value)

# Test LibreOffice conversion worker
def test_libreoffice_conversion_worker():
    """Test Office document conversion worker functionality."""
    # Create a worker with an Office document file
    worker = ConversionWorker("input.docx", "output.pdf")
    assert worker.file_path == "input.docx"
    assert worker.output_path == "output.pdf"
    
    # Test signals with mocks
    progress_mock = MagicMock()
    complete_mock = MagicMock()
    
    worker.update_progress.connect(progress_mock)
    worker.conversion_complete.connect(complete_mock)
    
    # Mock the LibreOffice conversion method to avoid actual conversion
    with patch.object(worker, 'convert_using_libreoffice') as mock_convert:
        with patch('time.sleep'):
            worker.run()
        
        # Verify the LibreOffice conversion method was called
        mock_convert.assert_called_once()
    
    # Verify signal was emitted
    complete_mock.assert_called_once()

# Test LibreOffice conversion method on different platforms
@pytest.mark.parametrize("platform_name,soffice_path", [
    ("Darwin", "/Applications/LibreOffice.app/Contents/MacOS/soffice"),
    ("Windows", "C:\\Program Files\\LibreOffice\\program\\soffice.exe"),
    ("Linux", "libreoffice")
])
def test_convert_using_libreoffice(platform_name, soffice_path):
    """Test the LibreOffice conversion method on different platforms."""
    worker = ConversionWorker("input.docx", "output.pdf")
    
    # Mock platform detection and path existence check
    with patch('platform.system', return_value=platform_name):
        with patch('os.path.exists', return_value=True):
            # Mock the subprocess run
            with patch('subprocess.run') as mock_run:
                # Mock os.rename to avoid actual file operations
                with patch('os.rename') as mock_rename:
                    # For Windows test case, we need to mock os.environ.get
                    if platform_name == "Windows":
                        with patch('os.environ.get', return_value="C:\\Program Files"):
                            # Also mock os.path.join to control path format
                            with patch('os.path.join', return_value="C:\\Program Files\\LibreOffice\\program\\soffice.exe"):
                                worker.convert_using_libreoffice()
                    else:
                        worker.convert_using_libreoffice()
                    
                    # Verify subprocess.run was called with correct arguments
                    mock_run.assert_called_once()
                    args = mock_run.call_args[0][0]
                    
                    # For Windows, do a flexible path check to handle slash differences
                    if platform_name == "Windows":
                        # Normalize both paths to handle slash differences
                        normalized_actual = args[0].replace('/', '\\')
                        assert normalized_actual == soffice_path
                    else:
                        assert args[0] == soffice_path  # Check executable path
                    
                    assert '--headless' in args
                    assert '--convert-to' in args
                    assert 'pdf' in args
                    assert '--outdir' in args

# Test LibreOffice not found error
def test_libreoffice_not_found():
    """Test error handling when LibreOffice is not found."""
    worker = ConversionWorker("input.docx", "output.pdf")
    
    # Mock platform detection (macOS in this case)
    with patch('platform.system', return_value="Darwin"):
        # Mock path existence check to return False (LibreOffice not found)
        with patch('os.path.exists', return_value=False):
            # Mock 'which' command to also fail finding LibreOffice
            with patch('subprocess.run', side_effect=Exception("Command not found")):
                # Test that exception is properly handled
                with pytest.raises(Exception) as excinfo:
                    worker.convert_using_libreoffice()
                
                # Verify error message
                assert "LibreOffice not found" in str(excinfo.value)

# Test LibreOffice conversion error
def test_libreoffice_conversion_error():
    """Test error handling in the LibreOffice conversion process."""
    worker = ConversionWorker("input.docx", "output.pdf")
    
    # Mock platform detection and path existence
    with patch('platform.system', return_value="Linux"):
        with patch('os.path.exists', return_value=True):
            # Mock subprocess.run to raise CalledProcessError
            with patch('subprocess.run', side_effect=subprocess.CalledProcessError(1, "libreoffice")):
                # Test that exception is properly handled
                with pytest.raises(Exception) as excinfo:
                    worker.convert_using_libreoffice()
                
                # Verify error message
                assert "LibreOffice conversion failed" in str(excinfo.value)