# Created 100% by AI
# test_app.py - Simplified tests for File2PDF
# Run with: pytest -v test_app.py

import os
import pytest
from unittest.mock import MagicMock, patch
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFileDialog

# Import the application to test
from app import PDFConverterApp, ConversionWorker

# Simple fixture for the app
@pytest.fixture
def app(qtbot):
    test_app = PDFConverterApp()
    qtbot.addWidget(test_app)
    return test_app

# Test basic app initialization
def test_app_initialization(app):
    """Test that the app initializes with the correct defaults."""
    assert app.windowTitle() == "FileConvert - PDF Creator"
    assert app.selected_file is None
    assert app.output_path is None
    assert not app.convert_button.isEnabled()
    assert app.file_label.text() == "No file selected"

# Test file browsing
def test_browse_file(app, qtbot, monkeypatch):
    """Test file selection functionality."""
    # Mock file dialog to return a test file path
    test_file = "/fake/path/document.txt"
    monkeypatch.setattr(QFileDialog, 'getOpenFileName', lambda *args, **kwargs: (test_file, '*'))
    
    # Click browse button
    qtbot.mouseClick(app.browse_button, Qt.LeftButton)
    
    # Verify file was selected
    assert app.selected_file == test_file
    assert app.file_label.text() == "document.txt"
    assert app.convert_button.isEnabled()

# Test output folder selection
def test_choose_output_folder(app, qtbot, monkeypatch):
    """Test output folder selection."""
    # Setup app with a file selected
    app.selected_file = "/fake/path/document.txt"
    
    # Mock folder dialog
    test_folder = "/fake/output/folder"
    monkeypatch.setattr(QFileDialog, 'getExistingDirectory', lambda *args, **kwargs: test_folder)
    
    # Click output folder button
    qtbot.mouseClick(app.output_button, Qt.LeftButton)
    
    # Verify output folder was set
    assert "Output folder: /fake/output/folder" in app.output_label.text()

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

# Test conversion process
def test_convert_to_pdf(app, qtbot, monkeypatch):
    """Test the conversion process."""
    # Setup app with a file selected
    app.selected_file = "/fake/path/document.txt"
    app.convert_button.setEnabled(True)
    
    # Mock worker thread to return immediately
    with patch('app.ConversionWorker.run'):
        # Start conversion
        qtbot.mouseClick(app.convert_button, Qt.LeftButton)
        
        # Check UI state during conversion
        assert not app.convert_button.isEnabled()
        assert app.status_label.text() == "Converting..."
        
        # Simulate conversion completion
        app.conversion_finished(True, "Success")
        
        # Check UI was updated correctly
        assert app.convert_button.isEnabled()
        assert "successful" in app.status_label.text().lower()

# Test error handling
def test_conversion_error(app, qtbot):
    """Test error handling in the conversion process."""
    app.conversion_finished(False, "Test error")
    assert "failed" in app.status_label.text().lower()
    assert "Test error" in app.status_label.text()