# Task 2: Simplify LibreOffice Path Detection

**Time:** 2-3 hours
**Difficulty:** Medium
**File:** `file_convert/src/app.py`

## Problem

The `convert_using_libreoffice()` method has like 40 lines just to find where LibreOffice is installed. It's nested and hard to read.

## What to change

### Step 1: Make a new method to find LibreOffice

Add this new method right after `convert_html_to_pdf()` (around line 178):

```python
def get_libreoffice_path(self):
    """Find LibreOffice on the system"""
    system = platform.system()

    # Possible paths for each OS
    if system == "Darwin":  # Mac
        paths = [
            "/Applications/LibreOffice.app/Contents/MacOS/soffice",
            "/Applications/LibreOffice.app/Contents/MacOS/soffice.bin",
        ]
    elif system == "Windows":
        program_files = os.environ.get("PROGRAMFILES", "C:\\Program Files")
        paths = [
            os.path.join(program_files, "LibreOffice", "program", "soffice.exe"),
        ]
    else:  # Linux
        paths = ["libreoffice"]

    # Check if any of these exist
    for path in paths:
        if os.path.exists(path):
            return path

    # For Linux, assume it's in PATH
    if system == "Linux":
        return "libreoffice"

    # Last try: use 'which' command on Mac/Linux
    if system in ["Darwin", "Linux"]:
        try:
            result = subprocess.run(['which', 'soffice'],
                                  capture_output=True,
                                  text=True,
                                  timeout=5)
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
        except:
            pass

    # Didn't find it
    raise Exception("LibreOffice not found. Install it to convert Office files.")
```

Test: Add a print statement to check it works:
```python
path = self.get_libreoffice_path()
print(f"Found LibreOffice: {path}")
```

### Step 2: Update convert_using_libreoffice to use it

Replace lines 180-223 with this simpler version:

```python
def convert_using_libreoffice(self, file_path, output_path):
    """Convert Office documents using LibreOffice"""
    self.update_progress.emit(20, self.current_file)

    # Find LibreOffice
    try:
        soffice_path = self.get_libreoffice_path()
    except Exception as e:
        raise Exception(str(e))

    output_dir = os.path.dirname(output_path)
    self.update_progress.emit(40, self.current_file)

    # Convert the file
    try:
        subprocess.run([
            soffice_path,
            '--headless',
            '--convert-to', 'pdf',
            '--outdir', output_dir,
            file_path
        ], check=True, timeout=120)

        self.update_progress.emit(80, self.current_file)

        # Rename if needed
        base_name = os.path.basename(file_path)
        file_name = os.path.splitext(base_name)[0]
        generated_pdf = os.path.join(output_dir, f"{file_name}.pdf")

        if os.path.exists(generated_pdf) and generated_pdf != output_path:
            os.rename(generated_pdf, output_path)

        self.update_progress.emit(100, self.current_file)

    except subprocess.TimeoutExpired:
        raise Exception("LibreOffice took too long (timeout)")
    except subprocess.CalledProcessError as e:
        raise Exception(f"LibreOffice conversion failed: {str(e)}")
```

## Test checklist

- [ ] Convert a .docx file
- [ ] Convert a .xlsx file
- [ ] Convert a .pptx file
- [ ] Error message if LibreOffice not installed
- [ ] Works on your OS (test on Mac, Windows, or Linux)

Now it's way cleaner - the path finding logic is separate and easier to update.
