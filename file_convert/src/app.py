#File2PDF - A simple file to PDF converter
# Author: Ankit Cherian

import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QLabel, 
                           QVBoxLayout, QHBoxLayout, QWidget, QFileDialog, 
                           QProgressBar, QMessageBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import subprocess
import platform
import time  
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

class ConversionWorker(QThread):
    """Worker thread to handle file conversion in the background"""
    update_progress = pyqtSignal(int)
    conversion_complete = pyqtSignal(bool, str)
    
    def __init__(self, file_path, output_path):
        super().__init__()
        self.file_path = file_path
        self.output_path = output_path
        
    def run(self):
        """Main method that runs when the thread starts"""
        try:
            file_extension = os.path.splitext(self.file_path)[1].lower()
            
            # Update progress
            self.update_progress.emit(10)
            time.sleep(0.5)  # Delay for UI feedback
            
            # Check file type and use appropriate conversion
            if file_extension in ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff']:
                self.convert_image_to_pdf()
            elif file_extension in ['.txt', '.md', '.csv']:
                self.convert_text_to_pdf()
            elif file_extension == '.html':
                self.convert_html_to_pdf()
            else:
                # For now, other file types aren't supported
                raise Exception(f"Unsupported file type: {file_extension}")
            
            self.conversion_complete.emit(True, "Conversion completed successfully!")
        except Exception as e:
            self.conversion_complete.emit(False, str(e))
            
    def convert_image_to_pdf(self):
        """Convert image to PDF using Pillow and reportlab"""
        try:
            self.update_progress.emit(30)
            
            # Open the image
            img = Image.open(self.file_path)
            width, height = img.size
            
            self.update_progress.emit(50)
            
            # Create a new PDF with reportlab
            c = canvas.Canvas(self.output_path, pagesize=(width, height))
            c.drawImage(self.file_path, 0, 0, width, height)
            
            self.update_progress.emit(80)
            
            # Save the PDF
            c.save()
            
            self.update_progress.emit(100)
        except Exception as e:
            raise Exception(f"Image conversion failed: {str(e)}")

    def convert_text_to_pdf(self):
        """Convert text files to PDF using reportlab"""
        try:
            self.update_progress.emit(30)
            
            # Open and read the text file
            with open(self.file_path, 'r', encoding='utf-8', errors='replace') as file:
                text = file.readlines()
            
            self.update_progress.emit(50)
            
            # Create PDF
            c = canvas.Canvas(self.output_path, pagesize=letter)
            width, height = letter


            try:
                pdfmetrics.registerFont(TTFont('Courier', 'Courier'))
                font_name = 'Courier'
            except:
                # Fallback to default font
                font_name = 'Helvetica'
            
            c.setFont(font_name, 10)
            
            self.update_progress.emit(70)
            
            # Write text to PDF
            y = height - inch  # Start position
            line_height = 14    # Space between lines
            margin = inch       # Page margin
            
            for line in text:
                if y < margin:  # If we've reached the bottom margin
                    c.showPage()
                    c.setFont(font_name, 10)
                    y = height - inch
                
                c.drawString(margin, y, line.rstrip('\n'))
                y -= line_height
            
            self.update_progress.emit(90)
            
            c.save()
            
            self.update_progress.emit(100)
        except Exception as e:
            raise Exception(f"Text conversion failed: {str(e)}")
            
    def convert_html_to_pdf(self):
        """Convert HTML to PDF using WeasyPrint or fallback to text conversion"""
        try:
            # First try to use WeasyPrint 
            try:
                import weasyprint
                
                self.update_progress.emit(30)
                
                # Read the HTML file
                with open(self.file_path, 'r', encoding='utf-8', errors='replace') as file:
                    html_content = file.read()
                
                self.update_progress.emit(60)
                
                # Convert HTML to PDF
                weasyprint.HTML(string=html_content).write_pdf(self.output_path)
                
                self.update_progress.emit(100)
            except (ImportError, OSError):
                self.convert_text_to_pdf()
        except Exception as e:
            raise Exception(f"HTML conversion failed: {str(e)}")

class PDFConverterApp(QMainWindow):
    """Main application window for PDF conversion"""
    
    def __init__(self):
        super().__init__()
        
        # Initialize variables
        self.selected_file = None
        self.output_path = None
        
        self._init_ui()
        self.setWindowTitle("FileConvert - PDF Creator")
        self.setMinimumSize(600, 400)
        
    def _init_ui(self):
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Create title
        title_label = QLabel("FileConvert - PDF Creator")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Create file selection area
        file_layout = QHBoxLayout()
        self.file_label = QLabel("No file selected")
        self.file_label.setStyleSheet("padding: 10px; background-color: #f0f0f0; border-radius: 5px;")
        file_layout.addWidget(self.file_label, 7)
        
        self.browse_button = QPushButton("Browse")
        self.browse_button.setStyleSheet("padding: 10px;")
        self.browse_button.clicked.connect(self.browse_file)
        file_layout.addWidget(self.browse_button, 3)
        
        main_layout.addLayout(file_layout)
        
        # Output directory selection
        output_layout = QHBoxLayout()
        self.output_label = QLabel("Output folder: Default (same as input)")
        self.output_label.setStyleSheet("padding: 10px; background-color: #f0f0f0; border-radius: 5px;")
        output_layout.addWidget(self.output_label, 7)
        
        self.output_button = QPushButton("Choose Folder")
        self.output_button.setStyleSheet("padding: 10px;")
        self.output_button.clicked.connect(self.choose_output_folder)
        output_layout.addWidget(self.output_button, 3)
        
        main_layout.addLayout(output_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setStyleSheet("margin-top: 20px;")
        main_layout.addWidget(self.progress_bar)
        
        # Supported file types info
        supported_label = QLabel("Supported file types:")
        supported_types = QLabel("Images: .jpg, .jpeg, .png, .bmp, .gif\nText: .txt, .md, .csv\nWeb: .html\nOther formats coming soon!")
        supported_types.setStyleSheet("color: #666;")
        
        main_layout.addWidget(supported_label)
        main_layout.addWidget(supported_types)
        
        # Convert button
        self.convert_button = QPushButton("Convert to PDF")
        self.convert_button.setStyleSheet("font-size: 18px; padding: 15px; background-color: #4CAF50; color: white;")
        self.convert_button.clicked.connect(self.convert_to_pdf)
        self.convert_button.setEnabled(False)
        main_layout.addWidget(self.convert_button)
        
        # Status label
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.status_label)
    
    def browse_file(self):
        """Open file browser to select input file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select File to Convert",
            "",
            "All Files (*);;Images (*.jpg *.jpeg *.png *.bmp *.gif);;Text Files (*.txt *.md *.csv)"
        )
        
        if file_path:
            self.selected_file = file_path
            self.file_label.setText(os.path.basename(file_path))
            self.convert_button.setEnabled(True)
            
            # Set default output path
            file_dir = os.path.dirname(file_path)
            file_name = os.path.splitext(os.path.basename(file_path))[0]
            self.output_path = os.path.join(file_dir, f"{file_name}.pdf")
    
    def choose_output_folder(self):
        """Open folder browser to select output directory"""
        output_dir = QFileDialog.getExistingDirectory(
            self,
            "Select Output Folder",
            os.path.dirname(self.selected_file) if self.selected_file else ""
        )
        
        if output_dir:
            if self.selected_file:
                file_name = os.path.splitext(os.path.basename(self.selected_file))[0]
                self.output_path = os.path.join(output_dir, f"{file_name}.pdf")
            
            self.output_label.setText(f"Output folder: {output_dir}")
    
    def convert_to_pdf(self):
        """Start the conversion process"""
        if not self.selected_file:
            QMessageBox.warning(self, "Error", "Please select a file to convert.")
            return
        
        # Prepare output path if not already set
        if not self.output_path:
            file_dir = os.path.dirname(self.selected_file)
            file_name = os.path.splitext(os.path.basename(self.selected_file))[0]
            self.output_path = os.path.join(file_dir, f"{file_name}.pdf")
        
        # Create and start the worker thread
        self.worker = ConversionWorker(self.selected_file, self.output_path)
        self.worker.update_progress.connect(self.update_progress)
        self.worker.conversion_complete.connect(self.conversion_finished)
        
        # Update UI
        self.convert_button.setEnabled(False)
        self.browse_button.setEnabled(False)
        self.output_button.setEnabled(False)
        self.status_label.setText("Converting...")
        self.status_label.setStyleSheet("color: blue;")
        
        # Start conversion
        self.worker.start()
    
    def update_progress(self, value):
        """Update progress bar value"""
        self.progress_bar.setValue(value)
    
    def conversion_finished(self, success, message):
        """Handle conversion completion"""
        # Re-enable UI
        self.convert_button.setEnabled(True)
        self.browse_button.setEnabled(True)
        self.output_button.setEnabled(True)
        
        if success:
            self.status_label.setText(f"Conversion successful! Saved to: {self.output_path}")
            self.status_label.setStyleSheet("color: green;")
            
        else:
            self.status_label.setText(f"Conversion failed: {message}")
            self.status_label.setStyleSheet("color: red;")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PDFConverterApp()
    window.show()
    sys.exit(app.exec_())