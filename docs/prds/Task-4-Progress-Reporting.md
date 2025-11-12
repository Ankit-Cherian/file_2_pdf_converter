# Task 4: Clean Up Progress Reporting

**Time:** 1-2 hours
**Difficulty:** Easy
**File:** `file_convert/src/app.py`

## Problem

Progress updates have random numbers everywhere:
- `self.update_progress.emit(30, ...)`
- `self.update_progress.emit(50, ...)`
- `self.update_progress.emit(80, ...)`

Hard to tell what these numbers mean or change them later.

## What to change

### Step 1: Make a helper method

Add this after `__init__` in the `ConversionWorker` class:

```python
def report_progress(self, step, total_steps):
    """Update progress bar based on which step we're on"""
    percentage = int((step / total_steps) * 100)
    percentage = min(100, max(0, percentage))  # Keep between 0-100
    self.update_progress.emit(percentage, self.current_file)
```

Test: Try calling it with `self.report_progress(1, 4)` - should show 25%.

### Step 2: Update convert_image_to_pdf

Replace the progress lines:

```python
def convert_image_to_pdf(self, file_path, output_path):
    """Convert image to PDF using Pillow and reportlab"""
    try:
        STEPS = 4

        # Open image
        self.report_progress(1, STEPS)
        img = Image.open(file_path)
        width, height = img.size

        # Create PDF
        self.report_progress(2, STEPS)
        c = canvas.Canvas(output_path, pagesize=(width, height))
        c.drawImage(file_path, 0, 0, width, height)

        # Save
        self.report_progress(3, STEPS)
        c.save()

        # Done
        self.report_progress(4, STEPS)
    except Exception as e:
        raise Exception(f"Image conversion failed: {str(e)}")
```

### Step 3: Update convert_text_to_pdf

Same idea - replace the progress emits:

```python
def convert_text_to_pdf(self, file_path, output_path):
    """Convert text files to PDF using reportlab"""
    try:
        STEPS = 5

        # Read file
        self.report_progress(1, STEPS)
        with open(file_path, 'r', encoding='utf-8', errors='replace') as file:
            text = file.readlines()

        # Setup PDF
        self.report_progress(2, STEPS)
        c = canvas.Canvas(output_path, pagesize=letter)
        # ... font setup code ...

        # Prepare layout
        self.report_progress(3, STEPS)
        y = height - inch
        line_height = 14
        margin = inch

        # Write text
        self.report_progress(4, STEPS)
        for line in text:
            # ... existing loop code ...

        # Save
        c.save()
        self.report_progress(5, STEPS)
    except Exception as e:
        raise Exception(f"Text conversion failed: {str(e)}")
```

### Step 4: Update convert_html_to_pdf

```python
def convert_html_to_pdf(self, file_path, output_path):
    """Convert HTML to PDF using WeasyPrint or fallback to text conversion"""
    try:
        try:
            import weasyprint
            STEPS = 3

            # Read HTML
            self.report_progress(1, STEPS)
            with open(file_path, 'r', encoding='utf-8', errors='replace') as file:
                html_content = file.read()

            # Convert
            self.report_progress(2, STEPS)
            weasyprint.HTML(string=html_content).write_pdf(output_path)

            # Done
            self.report_progress(3, STEPS)

        except (ImportError, OSError):
            self.convert_text_to_pdf(file_path, output_path)
    except Exception as e:
        raise Exception(f"HTML conversion failed: {str(e)}")
```

### Step 5: Update convert_using_libreoffice

```python
def convert_using_libreoffice(self, file_path, output_path):
    """Convert Office documents using LibreOffice"""
    STEPS = 4

    # Find LibreOffice
    self.report_progress(1, STEPS)
    try:
        soffice_path = self.get_libreoffice_path()
    except Exception as e:
        raise Exception(str(e))

    # Prepare
    self.report_progress(2, STEPS)
    output_dir = os.path.dirname(output_path)

    # Convert
    self.report_progress(3, STEPS)
    try:
        subprocess.run([
            soffice_path,
            '--headless',
            '--convert-to', 'pdf',
            '--outdir', output_dir,
            file_path
        ], check=True, timeout=120)

        # Handle output file
        base_name = os.path.basename(file_path)
        file_name = os.path.splitext(base_name)[0]
        generated_pdf = os.path.join(output_dir, f"{file_name}.pdf")

        if os.path.exists(generated_pdf) and generated_pdf != output_path:
            os.rename(generated_pdf, output_path)

        # Done
        self.report_progress(4, STEPS)

    except subprocess.CalledProcessError as e:
        raise Exception(f"LibreOffice conversion failed: {str(e)}")
```

## Test checklist

- [ ] Image conversion - progress bar moves smoothly
- [ ] Text conversion - progress bar moves smoothly
- [ ] Office doc - progress bar moves smoothly
- [ ] Progress reaches 100% each time
- [ ] No errors

Now it's clear what each progress value means - it's just "step X of Y"!
