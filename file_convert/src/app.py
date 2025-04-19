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
from pathlib import Path

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
            elif file_extension in ['.doc', '.docx', '.ppt', '.pptx', '.xls', '.xlsx', '.odt', '.ods', '.odp']:
                self.convert_using_libreoffice()
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

    def convert_using_libreoffice(self):
        """Convert Office documents using LibreOffice"""
        self.update_progress.emit(20)
        
        # Get LibreOffice executable path based on OS
        if platform.system() == "Darwin":  # macOS
            soffice_path = "/Applications/LibreOffice.app/Contents/MacOS/soffice"
            
            # If not found at default location, try to find it elsewhere
            if not os.path.exists(soffice_path):
                # Check some other common locations
                possible_paths = [
                    "/Applications/LibreOffice.app/Contents/MacOS/soffice.bin",
                    # Add more paths if needed
                ]
                
                for path in possible_paths:
                    if os.path.exists(path):
                        soffice_path = path
                        break
                        
                # If still not found, try using 'which' command
                if not os.path.exists(soffice_path):
                    try:
                        # Use subprocess to find the LibreOffice binary
                        result = subprocess.run(['which', 'soffice'], 
                                              capture_output=True, 
                                              text=True)
                        if result.returncode == 0 and result.stdout.strip():
                            soffice_path = result.stdout.strip()
                    except Exception:
                        pass
                        
        elif platform.system() == "Windows":
            # Windows typically has LibreOffice in Program Files
            program_files = os.environ.get("PROGRAMFILES", "C:\\Program Files")
            soffice_path = os.path.join(program_files, "LibreOffice", "program", "soffice.exe")
        else:  # Linux
            # Linux typically has it in the PATH
            soffice_path = "libreoffice"
        
        # Make sure LibreOffice exists
        if not os.path.exists(soffice_path) and platform.system() != "Linux":
            raise Exception("LibreOffice not found. Please install LibreOffice to convert Office documents.")
        
        output_dir = os.path.dirname(self.output_path)
        
        self.update_progress.emit(40)
        
        # Run LibreOffice to convert the file
        try:
            subprocess.run([
                soffice_path,
                '--headless',
                '--convert-to', 'pdf',
                '--outdir', output_dir,
                self.file_path
            ], check=True)
            
            self.update_progress.emit(80)
            
            # Rename the output file if needed
            base_name = os.path.basename(self.file_path)
            file_name_without_ext = os.path.splitext(base_name)[0]
            generated_pdf = os.path.join(output_dir, f"{file_name_without_ext}.pdf")
            
            if os.path.exists(generated_pdf) and generated_pdf != self.output_path:
                os.rename(generated_pdf, self.output_path)
                
            self.update_progress.emit(100)
        except subprocess.CalledProcessError as e:
            raise Exception(f"LibreOffice conversion failed: {str(e)}")

class PDFConverterApp(QMainWindow):
    """Main application window for PDF conversion"""
    
    def __init__(self):
        super().__init__()
        
        # Initialize variables
        self.selected_file = None
        self.output_path = None
        
        self._init_ui()
        self.setWindowTitle("FileConvert - Professional PDF Creator")
        self.setGeometry(100, 100, 650, 500)
        
    def _init_ui(self):
        # Basic Window Setup
        self.setWindowTitle("File2PDF: PDF Converter") # Slightly updated title
        self.setGeometry(100, 100, 650, 500) 
        
        # Color Palette & Styles
        COLOR_BACKGROUND = "#f8f9fa"  # Light gray background
        COLOR_WIDGET_BG = "#e9ecef"   # Slightly darker for input areas
        COLOR_BORDER = "#ced4da"      # Subtle border color
        COLOR_PRIMARY = "#007bff"     # Blue for the main button
        COLOR_PRIMARY_HOVER = "#0056b3" # Darker blue on hover
        COLOR_TEXT = "#212529"        # Dark text color
        COLOR_TEXT_SECONDARY = "#6c757d" # Lighter text for info
        COLOR_SUCCESS = "#28a745"     # Green for success status
        COLOR_ERROR = "#dc3545"       # Red for error status
        COLOR_INFO = "#17a2b8"        # Blue for info/converting status

        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {COLOR_BACKGROUND};
            }}
            QWidget {{
                color: {COLOR_TEXT}; /* Default text color */
            }}
            QLabel {{
                background-color: transparent; /* Ensure labels don't have unexpected backgrounds */
            }}
            QPushButton {{
                background-color: {COLOR_WIDGET_BG};
                color: {COLOR_TEXT};
                border: 1px solid {COLOR_BORDER};
                padding: 10px 15px; /* Increased padding */
                border-radius: 4px; /* Rounded corners */
                font-size: 14px; /* Consistent font size */
            }}
            QPushButton:hover {{
                background-color: #dee2e6; /* Slightly darker on hover */
                border-color: #adb5bd;
            }}
            QPushButton#ConvertButton {{ /* Specific style for the main button */
                background-color: {COLOR_PRIMARY};
                color: white;
                font-size: 16px; /* Larger font */
                font-weight: bold;
                padding: 12px 20px;
            }}
            QPushButton#ConvertButton:hover {{
                background-color: {COLOR_PRIMARY_HOVER};
                border-color: {COLOR_PRIMARY_HOVER};
            }}
            QPushButton:disabled {{ /* Style for disabled buttons */
                background-color: #e9ecef;
                color: #adb5bd;
            }}
            QLabel#FileLabel, QLabel#OutputLabel {{ /* Style for the file/output display labels */
                background-color: {COLOR_WIDGET_BG};
                border: 1px solid {COLOR_BORDER};
                padding: 10px;
                border-radius: 4px;
                font-size: 14px;
            }}
            QProgressBar {{
                border: 1px solid {COLOR_BORDER};
                border-radius: 4px;
                text-align: center;
                background-color: {COLOR_WIDGET_BG};
                height: 25px; /* Slightly taller */
            }}
            QProgressBar::chunk {{
                background-color: {COLOR_PRIMARY};
                border-radius: 4px; /* Match outer radius */
                margin: 1px; /* Small margin around the chunk */
            }}
            QLabel#StatusLabel {{ /* Prepare status label for colors */
                font-size: 14px;
                font-weight: bold;
                padding-top: 10px;
            }}
            QLabel#TitleLabel {{ /* Style the main title */
                font-size: 26px;
                font-weight: bold;
                color: {COLOR_TEXT};
                padding-bottom: 10px; /* Add space below title */
            }}
             QLabel#SupportedLabel {{ /* Style for the 'Supported types' header */
                font-size: 14px;
                font-weight: bold;
                margin-top: 10px;
            }}
            QLabel#SupportedTypes {{ /* Style for the list of types */
                color: {COLOR_TEXT_SECONDARY};
                font-size: 12px;
                line-height: 1.5; /* Improve readability */
            }}
        """)

        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(25, 25, 25, 25) # Slightly more margin
        main_layout.setSpacing(15) # Consistent spacing between elements

        # UI Elements
        
        # Create title
        title_label = QLabel("File2PDF: PDF Converter")
        title_label.setObjectName("TitleLabel") # Assign object name for specific styling
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Create file selection area
        file_layout = QHBoxLayout()
        file_layout.setSpacing(10) # Space between label and button
        self.file_label = QLabel("No file selected")
        self.file_label.setObjectName("FileLabel") # Assign object name
        file_layout.addWidget(self.file_label, 7) # Give label more horizontal space
        
        self.browse_button = QPushButton("Browse...") # Added ellipsis
        self.browse_button.clicked.connect(self.browse_file)
        file_layout.addWidget(self.browse_button, 3) # Button takes less space
        
        main_layout.addLayout(file_layout)
        
        # Output directory selection
        output_layout = QHBoxLayout()
        output_layout.setSpacing(10)
        self.output_label = QLabel("Output folder: Default (same as input)")
        self.output_label.setObjectName("OutputLabel")
        output_layout.addWidget(self.output_label, 7)
        
        self.output_button = QPushButton("Choose Folder...")
        self.output_button.clicked.connect(self.choose_output_folder)
        output_layout.addWidget(self.output_button, 3)
        
        main_layout.addLayout(output_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        main_layout.addWidget(self.progress_bar)
        
        # Supported file types info
        supported_label = QLabel("Supported file types:")
        supported_label.setObjectName("SupportedLabel")
        supported_types = QLabel("Documents: .doc, .docx, .odt, .txt, .md\nPresentations: .ppt, .pptx, .odp\nSpreadsheets: .xls, .xlsx, .ods\nImages: .jpg, .png, .bmp, .gif\nOthers: .html, .csv")
        supported_types.setObjectName("SupportedTypes")
        
        main_layout.addWidget(supported_label)
        main_layout.addWidget(supported_types)
        # This will add a stretchable space before the convert button and status
        main_layout.addStretch(1)
        
        # Convert button
        self.convert_button = QPushButton("Convert to PDF")
        self.convert_button.setObjectName("ConvertButton") # Assign object name
        self.convert_button.clicked.connect(self.convert_to_pdf)
        self.convert_button.setEnabled(False)
        main_layout.addWidget(self.convert_button)
        
        # Status label
        self.status_label = QLabel("")
        self.status_label.setObjectName("StatusLabel") # Assign object name
        self.status_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.status_label)
    
    def browse_file(self):
        """Open file browser to select input file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select File to Convert",
            "",
            "All Files (*);;Images (*.jpg *.jpeg *.png *.bmp *.gif);;Text Files (*.txt *.md *.csv);;Office Documents (*.doc *.docx *.ppt *.pptx *.xls *.xlsx *.odt *.ods *.odp)"
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
        
        # Define the color constant for consistent styling
        COLOR_INFO = "#17a2b8"
        
        # Update UI
        self.convert_button.setEnabled(False)
        self.browse_button.setEnabled(False)
        self.output_button.setEnabled(False)
        self.status_label.setText("Converting...")
        self.status_label.setStyleSheet(f"color: {COLOR_INFO};")
        
        # Start conversion
        self.worker.start()
    
    def update_progress(self, value):
        """Update progress bar value"""
        self.progress_bar.setValue(value)
    
    def conversion_finished(self, success, message):
        """Handle conversion completion"""
        self.convert_button.setEnabled(True)
        self.browse_button.setEnabled(True)
        self.output_button.setEnabled(True)
        
        COLOR_SUCCESS = "#28a745" 
        COLOR_ERROR = "#dc3545"  
        COLOR_INFO = "#17a2b8"   

        if success:
            self.status_label.setText(f"Conversion successful! Saved to: {self.output_path}")
            # Use the color constant
            self.status_label.setStyleSheet(f"color: {COLOR_SUCCESS};") 
            
            # Ask if the user wants to open the PDF
            reply = QMessageBox.question(
                self,
                "Conversion Complete",
                f"PDF created successfully at:\n{self.output_path}\n\nWould you like to open it?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            
            if reply == QMessageBox.Yes:
                self.open_file(self.output_path)
        else:
            self.status_label.setText(f"Conversion failed: {message}")
            # Use the color constant
            self.status_label.setStyleSheet(f"color: {COLOR_ERROR};")
            
            QMessageBox.critical(
                self,
                "Conversion Failed",
                f"Error: {message}\n\nPlease check the file type and ensure all necessary software (like LibreOffice) is installed correctly."
            )

    def open_file(self, file_path):
        """Open the created PDF file"""
        try:
            if platform.system() == "Darwin":  # macOS
                subprocess.call(["open", file_path])
            elif platform.system() == "Windows":
                os.startfile(file_path)
            else:  # Linux
                subprocess.call(["xdg-open", file_path])
        except Exception as e:
            QMessageBox.warning(
                self,
                "Error Opening File",
                f"Could not open the PDF file: {str(e)}\n\nThe file was created successfully, but you'll need to open it manually."
            )

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PDFConverterApp()
    window.show()
    sys.exit(app.exec_())