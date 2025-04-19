
# File2PDF Converter 

This app converts different types of files to PDF format without needing to use online services or paying for software. All conversions happen directly on your computer - your files are never uploaded to any servers or shared with anyone.

## Supported File Types

- **Documents**: .doc, .docx, .odt, .txt, .md
- **Presentations**: .ppt, .pptx, .odp
- **Spreadsheets**: .xls, .xlsx, .ods
- **Images**: .jpg, .png, .bmp, .gif
- **Text**: .html, .csv

## System Requirements

- **Windows**: Windows 10 or newer
- **Mac**: macOS 10.13 (High Sierra) or newer
- **Linux**: Most modern distributions
- **Disk Space**: At least 500 MB free space for the app and its dependencies

## How to Download and Run the App 

### Step 1: Download the Files from GitHub
1. Look for the green "Code" button and click it
2. Click "Download ZIP" from the dropdown menu
3. Find the downloaded ZIP file on your computer (usually in your Downloads folder)
4. Right-click the ZIP file and select "Extract All..." or "Unzip"
5. Choose where to extract the files (like your Desktop for easy access)
6. Click "Extract"

### Step 2: Install Python Using the Terminal
1. Open your computer's command prompt or terminal:
   - **Windows**: Press the Windows key, type "cmd" and press Enter
   - **Mac**: Press Command+Space, type "terminal" and press Enter
   - **Linux**: Press Ctrl+Alt+T

2. Install Python based on your operating system:
   
   **On macOS**:
   ```
   brew install python
   ```
   (If you don't have Homebrew, install it first with: `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`)

   **On Windows**:
   Windows users should download and run the installer from python.org as it's more reliable:
   1. Go to https://www.python.org/downloads/
   2. Download the latest Python version
   3. Run the installer and check "Add Python to PATH"
   4. Click "Install Now"

3. Verify Python is installed correctly:
   ```
   python --version
   ```
   or on some systems:
   ```
   python3 --version
   ```
   You should see a version number like `Python 3.x.x`

### Step 3: Install the Required Programs
1. Navigate to the folder where you put the files:
   ```
   cd path/to/extracted/folder
   ```
   (For example, if its in downloads: `cd downloads/file2pdf`)

2. Install the required packages by typing this command and pressing Enter:
   ```
   pip install -r requirements.txt
   ```

   Wait for the installation to complete (this might take a few minutes)

3. Install LibreOffice (needed for converting Word, Excel, and PowerPoint files):
   
   **On macOS**:
   ```
   brew install --cask libreoffice
   ```

   **On Windows**:
   Download from https://www.libreoffice.org/download/download/ and follow the installation wizard

### Step 4: Run the App
1. Navigate to the program folder:
   ```
   cd path/to/extracted/folder/file_convert/src
   ```
2. Run the app by typing:
   ```
   python app.py
   ```
   or on some systems:
   ```
   python3 app.py
   ```
3. The File2PDF app should now be open.

## Quick Start (For Experienced Users)

If you're comfortable with command line and Python:

1. Clone the repository: `git clone https://github.com/ankitcherian/file2pdf.git`
2. Install requirements: `pip install -r requirements.txt`
3. Install LibreOffice if needed for office document conversion
4. Run the app: `python file_convert/src/app.py`

## How to Use the App

1. When the app opens, click the "Browse..." button to find the file you want to convert
2. Select the file and click "Open"
3. If you want to save the PDF in a specific folder, click "Choose Folder..." otherwise, it will save in the same folder as your original file.
4. Click the "Convert to PDF" button
5. Wait for the conversion to finish
6. When it's done, you'll see a message asking if you want to open the PDF - click "Yes" to view it

## Common Problems

- **Python not found**: Check if Python is in your PATH by typing `python --version` or `python3 --version`
- **Missing packages**: Make sure you ran `pip install -r requirements.txt` correctly
- **Office documents won't convert**: Make sure LibreOffice is installed
- **App won't start**: Make sure you're in the correct folder when running `python app.py`
  
