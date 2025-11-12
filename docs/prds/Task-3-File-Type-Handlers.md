# Task 3: Better File Type Handler System

**Time:** 3-4 hours
**Difficulty:** Medium
**File:** `file_convert/src/app.py`

## Problem

The code that decides which converter to use (lines 52-62) is a long if-elif chain. Plus the file extensions are listed in multiple places - in the code, in the file dialog, and in the UI text.

Makes it annoying to add new file types.

## What to change

### Step 1: Make a format map

At the top of the `ConversionWorker` class (after line 21), add:

```python
class ConversionWorker(QThread):
    """Worker thread to handle file conversion in the background"""

    # Maps file extensions to their conversion methods
    FILE_FORMATS = {
        'images': {
            'extensions': ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff'],
            'handler': 'convert_image_to_pdf',
            'name': 'Images'
        },
        'text': {
            'extensions': ['.txt', '.md', '.csv'],
            'handler': 'convert_text_to_pdf',
            'name': 'Text files'
        },
        'html': {
            'extensions': ['.html', '.htm'],
            'handler': 'convert_html_to_pdf',
            'name': 'HTML files'
        },
        'office': {
            'extensions': ['.doc', '.docx', '.odt', '.xls', '.xlsx', '.ods',
                          '.ppt', '.pptx', '.odp'],
            'handler': 'convert_using_libreoffice',
            'name': 'Office documents'
        }
    }

    update_progress = pyqtSignal(int, str)
    # ... rest of code
```

Test: App still launches.

### Step 2: Add helper method

After the `__init__` method, add:

```python
def get_handler_for_file(self, extension):
    """Figure out which converter to use for this file type"""
    ext_lower = extension.lower()

    # Look through all the formats we support
    for format_info in self.FILE_FORMATS.values():
        if ext_lower in format_info['extensions']:
            method_name = format_info['handler']
            return getattr(self, method_name)

    # Not supported
    raise ValueError(f"Can't convert {extension} files yet")
```

Test: Try calling it:
```python
handler = self.get_handler_for_file('.jpg')
print(handler.__name__)  # Should print: convert_image_to_pdf
```

### Step 3: Replace the if-elif chain

In the `run()` method, replace lines 52-62 with:

```python
# Find the right handler for this file type
try:
    handler = self.get_handler_for_file(file_extension)
    handler(file_path, output_path)
except ValueError as e:
    raise Exception(str(e))
```

Way simpler!

Test: Try converting different file types.

### Step 4 (Optional): Update file dialog

If you want, you can make the file dialog use this format list too. In `browse_files()` method (line 474):

```python
# Build filters from the format list
filters = ["All Files (*)"]
for fmt in ConversionWorker.FILE_FORMATS.values():
    extensions = ' '.join([f"*{ext}" for ext in fmt['extensions']])
    filters.append(f"{fmt['name']} ({extensions})")

file_paths, _ = QFileDialog.getOpenFileNames(
    self,
    "Select Files to Convert",
    "",
    ";;".join(filters)
)
```

### Step 5 (Optional): Update supported types display

In `_init_ui()`, around line 448, make it dynamic:

```python
# Show supported types
type_lines = []
for fmt in ConversionWorker.FILE_FORMATS.values():
    exts = ', '.join(fmt['extensions'])
    type_lines.append(f"{fmt['name']}: {exts}")

supported_types = QLabel('\n'.join(type_lines))
```

## Test checklist

- [ ] Convert image file
- [ ] Convert text file
- [ ] Convert office doc
- [ ] Try unsupported file type (shows error)
- [ ] File dialog shows file types
- [ ] Supported types list shows correctly

Now adding a new file type is just one entry in the FILE_FORMATS dict!
