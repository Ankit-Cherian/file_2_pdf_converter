#File2PDF - A simple file to PDF converter
# Author: Ankit Cherian

import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QLabel, 
                           QVBoxLayout, QHBoxLayout, QWidget, QFileDialog, 
                           QProgressBar, QMessageBox, QListWidget, QFrame)
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
    update_progress = pyqtSignal(int, str)
    conversion_complete = pyqtSignal(bool, str)
    file_complete = pyqtSignal(str, bool, str)
    
    def __init__(self, file_paths, output_dir):
        super().__init__()
        self.file_paths = file_paths
        self.output_dir = output_dir
        self.current_file = ""
        
    def run(self):
        """Main method that runs when the thread starts"""
        overall_success = True
        error_messages = []
        
        total_files = len(self.file_paths)
        for i, file_path in enumerate(self.file_paths):
            try:
                self.current_file = os.path.basename(file_path)
                file_extension = os.path.splitext(file_path)[1].lower()
                
                # Calculate output path
                file_name = os.path.splitext(os.path.basename(file_path))[0]
                output_path = os.path.join(self.output_dir, f"{file_name}.pdf")
                
                # Update progress
                self.update_progress.emit(5, self.current_file)
                
                # Check file type and use appropriate conversion
                if file_extension in ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff']:
                    self.convert_image_to_pdf(file_path, output_path)
                elif file_extension in ['.txt', '.md', '.csv']:
                    self.convert_text_to_pdf(file_path, output_path)
                elif file_extension == '.html':
                    self.convert_html_to_pdf(file_path, output_path)
                elif file_extension in ['.doc', '.docx', '.ppt', '.pptx', '.xls', '.xlsx', '.odt', '.ods', '.odp']:
                    self.convert_using_libreoffice(file_path, output_path)
                else:
                    # For now, other file types aren't supported
                    raise Exception(f"Unsupported file type: {file_extension}")
                
                # Signal completion of this file
                self.file_complete.emit(self.current_file, True, output_path)
                
            except Exception as e:
                error_message = f"Failed to convert {os.path.basename(file_path)}: {str(e)}"
                error_messages.append(error_message)
                overall_success = False
                self.file_complete.emit(self.current_file, False, str(e))
            
            # Update progress for next file
            progress_percentage = int(((i + 1) / total_files) * 100)
            self.update_progress.emit(progress_percentage, "")
        
        # Signal overall completion
        if overall_success:
            self.conversion_complete.emit(True, "All conversions completed successfully!")
        else:
            self.conversion_complete.emit(False, "\n".join(error_messages))
            
    def convert_image_to_pdf(self, file_path, output_path):
        """Convert image to PDF using Pillow and reportlab"""
        try:
            self.update_progress.emit(30, self.current_file)
            
            # Open the image
            img = Image.open(file_path)
            width, height = img.size
            
            self.update_progress.emit(50, self.current_file)
            
            # Create a new PDF with reportlab
            c = canvas.Canvas(output_path, pagesize=(width, height))
            c.drawImage(file_path, 0, 0, width, height)
            
            self.update_progress.emit(80, self.current_file)
            
            # Save the PDF
            c.save()
            
            self.update_progress.emit(100, self.current_file)
        except Exception as e:
            raise Exception(f"Image conversion failed: {str(e)}")

    def convert_text_to_pdf(self, file_path, output_path):
        """Convert text files to PDF using reportlab"""
        try:
            self.update_progress.emit(30, self.current_file)
            
            # Open and read the text file
            with open(file_path, 'r', encoding='utf-8', errors='replace') as file:
                text = file.readlines()
            
            self.update_progress.emit(50, self.current_file)
            
            # Create PDF
            c = canvas.Canvas(output_path, pagesize=letter)
            width, height = letter


            try:
                pdfmetrics.registerFont(TTFont('Courier', 'Courier'))
                font_name = 'Courier'
            except:
                # Fallback to default font
                font_name = 'Helvetica'
            
            c.setFont(font_name, 10)
            
            self.update_progress.emit(70, self.current_file)
            
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
            
            self.update_progress.emit(90, self.current_file)
            
            c.save()
            
            self.update_progress.emit(100, self.current_file)
        except Exception as e:
            raise Exception(f"Text conversion failed: {str(e)}")
            
    def convert_html_to_pdf(self, file_path, output_path):
        """Convert HTML to PDF using WeasyPrint or fallback to text conversion"""
        try:
            # First try to use WeasyPrint 
            try:
                import weasyprint
                
                self.update_progress.emit(30, self.current_file)
                
                # Read the HTML file
                with open(file_path, 'r', encoding='utf-8', errors='replace') as file:
                    html_content = file.read()
                
                self.update_progress.emit(60, self.current_file)
                
                # Convert HTML to PDF
                weasyprint.HTML(string=html_content).write_pdf(output_path)
                
                self.update_progress.emit(100, self.current_file)
            except (ImportError, OSError):
                self.convert_text_to_pdf(file_path, output_path)
        except Exception as e:
            raise Exception(f"HTML conversion failed: {str(e)}")

    def convert_using_libreoffice(self, file_path, output_path):
        """Convert Office documents using LibreOffice"""
        self.update_progress.emit(20, self.current_file)
        
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
        
        output_dir = os.path.dirname(output_path)
        
        self.update_progress.emit(40, self.current_file)
        
        # Run LibreOffice to convert the file
        try:
            subprocess.run([
                soffice_path,
                '--headless',
                '--convert-to', 'pdf',
                '--outdir', output_dir,
                file_path
            ], check=True)
            
            self.update_progress.emit(80, self.current_file)
            
            # Rename the output file if needed
            base_name = os.path.basename(file_path)
            file_name_without_ext = os.path.splitext(base_name)[0]
            generated_pdf = os.path.join(output_dir, f"{file_name_without_ext}.pdf")
            
            if os.path.exists(generated_pdf) and generated_pdf != output_path:
                os.rename(generated_pdf, output_path)
                
            self.update_progress.emit(100, self.current_file)
        except subprocess.CalledProcessError as e:
            raise Exception(f"LibreOffice conversion failed: {str(e)}")

class PDFConverterApp(QMainWindow):
    """Main application window for PDF conversion"""
    
    def __init__(self):
        super().__init__()
        
        # Initialize variables
        self.selected_files = []
        self.output_dir = None
        self.converted_files = {}  # Track conversion status for each file
        self.MAX_FILES = 20  # Maximum number of files allowed
        
        self._init_ui()
        self.setWindowTitle("FileConvert - Professional PDF Creator")
        self.setGeometry(100, 100, 650, 550)  # Made slightly taller for file list
        
    def _init_ui(self):
        # Basic Window Setup
        self.setWindowTitle("File2PDF: Multi-File Converter")  # Updated title
        self.setGeometry(100, 100, 650, 550)  # Made taller for file list
        
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
            QListWidget {{ /* Style for the file list */
                background-color: {COLOR_WIDGET_BG};
                border: 1px solid {COLOR_BORDER};
                border-radius: 4px;
                padding: 5px;
            }}
            QFrame#FilesFrame {{ /* Style for the files section */
                border: 1px solid {COLOR_BORDER};
                border-radius: 4px;
                background-color: {COLOR_WIDGET_BG};
                padding: 10px;
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
        title_label = QLabel("File2PDF: Multi-File Converter")  # Updated title
        title_label.setObjectName("TitleLabel") # Assign object name for specific styling
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Create file selection frame
        files_frame = QFrame()
        files_frame.setObjectName("FilesFrame")
        files_layout = QVBoxLayout(files_frame)
        
        # File selection header
        files_header = QHBoxLayout()
        file_count_label = QLabel("Selected files: 0")
        files_header.addWidget(file_count_label)
        
        self.browse_button = QPushButton("Add Files...")
        self.browse_button.clicked.connect(self.browse_files)
        files_header.addWidget(self.browse_button)
        
        clear_button = QPushButton("Clear All")
        clear_button.clicked.connect(self.clear_files)
        files_header.addWidget(clear_button)
        
        files_layout.addLayout(files_header)
        
        # File list widget
        self.file_list = QListWidget()
        self.file_list.setMinimumHeight(120)  # Set minimum height for list
        files_layout.addWidget(self.file_list)
        
        main_layout.addWidget(files_frame)
        
        # Output directory selection
        output_layout = QHBoxLayout()
        output_layout.setSpacing(10)
        self.output_label = QLabel("Output folder: Default (same as first input)")
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
        
        # Current file label
        self.current_file_label = QLabel("")
        self.current_file_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.current_file_label)
        
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
        self.convert_button = QPushButton("Convert All to PDF")  # Updated button text
        self.convert_button.setObjectName("ConvertButton") # Assign object name
        self.convert_button.clicked.connect(self.convert_to_pdf)
        self.convert_button.setEnabled(False)
        main_layout.addWidget(self.convert_button)
        
        # Status label
        self.status_label = QLabel("")
        self.status_label.setObjectName("StatusLabel") # Assign object name
        self.status_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.status_label)
        
        # Store references to elements we'll need to update
        self.file_count_label = file_count_label
    
    def browse_files(self):
        """Open file browser to select multiple input files"""
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Files to Convert",
            "",
            "All Files (*);;Images (*.jpg *.jpeg *.png *.bmp *.gif);;Text Files (*.txt *.md *.csv);;Office Documents (*.doc *.docx *.ppt *.pptx *.xls *.xlsx *.odt *.ods *.odp)"
        )
        
        if file_paths:
            # Check if adding these files would exceed the maximum
            if len(self.selected_files) + len(file_paths) > self.MAX_FILES:
                QMessageBox.warning(
                    self, 
                    "Too Many Files", 
                    f"You can select a maximum of {self.MAX_FILES} files. Only the first {self.MAX_FILES - len(self.selected_files)} files will be added."
                )
                file_paths = file_paths[:self.MAX_FILES - len(self.selected_files)]
            
            # Add files to the list
            for file_path in file_paths:
                if file_path not in self.selected_files:
                    self.selected_files.append(file_path)
                    self.file_list.addItem(os.path.basename(file_path))
            
            # Update file count
            self.file_count_label.setText(f"Selected files: {len(self.selected_files)}")
            
            # Enable convert button if there are files selected
            self.convert_button.setEnabled(len(self.selected_files) > 0)
            
            # Set default output directory if not already set
            if not self.output_dir and self.selected_files:
                self.output_dir = os.path.dirname(self.selected_files[0])
                self.output_label.setText(f"Output folder: {self.output_dir}")
    
    def clear_files(self):
        """Clear all selected files"""
        self.selected_files = []
        self.file_list.clear()
        self.file_count_label.setText("Selected files: 0")
        self.convert_button.setEnabled(False)
        self.converted_files = {}
    
    def choose_output_folder(self):
        """Open folder browser to select output directory"""
        output_dir = QFileDialog.getExistingDirectory(
            self,
            "Select Output Folder",
            self.output_dir if self.output_dir else (os.path.dirname(self.selected_files[0]) if self.selected_files else "")
        )
        
        if output_dir:
            self.output_dir = output_dir
            self.output_label.setText(f"Output folder: {output_dir}")
    
    def convert_to_pdf(self):
        """Start the conversion process for all selected files"""
        if not self.selected_files:
            QMessageBox.warning(self, "Error", "Please select at least one file to convert.")
            return
        
        # Ensure output directory is set
        if not self.output_dir:
            self.output_dir = os.path.dirname(self.selected_files[0])
        
        # Create and start the worker thread
        self.worker = ConversionWorker(self.selected_files, self.output_dir)
        self.worker.update_progress.connect(self.update_progress)
        self.worker.conversion_complete.connect(self.conversion_finished)
        self.worker.file_complete.connect(self.file_conversion_finished)
        
        # Reset converted files tracking
        self.converted_files = {file_path: {'status': 'pending', 'output': ''} for file_path in self.selected_files}
        
        # Define the color constant for consistent styling
        COLOR_INFO = "#17a2b8"
        
        # Update UI
        self.convert_button.setEnabled(False)
        self.browse_button.setEnabled(False)
        self.output_button.setEnabled(False)
        self.status_label.setText("Converting files...")
        self.status_label.setStyleSheet(f"color: {COLOR_INFO};")
        
        # Start conversion
        self.worker.start()
    
    def update_progress(self, value, current_file):
        """Update progress bar value and current file label"""
        self.progress_bar.setValue(value)
        if current_file:
            self.current_file_label.setText(f"Converting: {current_file}")
    
    def file_conversion_finished(self, filename, success, message):
        """Handle completion of a single file conversion"""
        # Find the file path from filename
        file_path = next((path for path in self.selected_files if os.path.basename(path) == filename), None)
        
        if file_path:
            # Update status for this file
            self.converted_files[file_path] = {
                'status': 'success' if success else 'failed',
                'output': message
            }
            
            # Update the item in the list with status indicator
            for i in range(self.file_list.count()):
                if self.file_list.item(i).text() == filename:
                    status_prefix = "✅ " if success else "❌ "
                    self.file_list.item(i).setText(f"{status_prefix}{filename}")
                    break
    
    def conversion_finished(self, overall_success, message):
        """Handle conversion completion of all files"""
        self.convert_button.setEnabled(True)
        self.browse_button.setEnabled(True)
        self.output_button.setEnabled(True)
        self.current_file_label.setText("")
        
        COLOR_SUCCESS = "#28a745" 
        COLOR_ERROR = "#dc3545"  
        COLOR_INFO = "#17a2b8"   

        if overall_success:
            self.status_label.setText("All files converted successfully!")
            self.status_label.setStyleSheet(f"color: {COLOR_SUCCESS};")
            
            # Calculate success count
            success_count = sum(1 for file_info in self.converted_files.values() if file_info['status'] == 'success')
            
            # Ask if the user wants to open the output folder
            reply = QMessageBox.question(
                self,
                "Conversion Complete",
                f"Successfully converted {success_count} files to PDF.\nFiles were saved to: {self.output_dir}\n\nWould you like to open the output folder?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            
            if reply == QMessageBox.Yes:
                self.open_folder(self.output_dir)
        else:
            # Count successes and failures
            success_count = sum(1 for file_info in self.converted_files.values() if file_info['status'] == 'success')
            fail_count = sum(1 for file_info in self.converted_files.values() if file_info['status'] == 'failed')
            
            self.status_label.setText(f"Conversion completed with {fail_count} errors")
            self.status_label.setStyleSheet(f"color: {COLOR_ERROR};")
            
            QMessageBox.warning(
                self,
                "Conversion Results",
                f"Converted {success_count} files successfully.\n{fail_count} files failed to convert.\n\nCheck the file list for details."
            )

    def open_folder(self, folder_path):
        """Open the specified folder"""
        try:
            if platform.system() == "Darwin":  # macOS
                subprocess.call(["open", folder_path])
            elif platform.system() == "Windows":
                os.startfile(folder_path)
            else:  # Linux
                subprocess.call(["xdg-open", folder_path])
        except Exception as e:
            QMessageBox.warning(
                self,
                "Error Opening Folder",
                f"Could not open the folder: {str(e)}\n\nPlease navigate to it manually at:\n{folder_path}"
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