# Task 1: Move Color Codes to One Place

**Time:** 1-2 hours
**Difficulty:** Easy
**File:** `file_convert/src/app.py`

## Problem

Right now the same color codes are written in 3 different places:
- Lines 275-284 in `_init_ui()`
- Line 548 in `convert_to_pdf()`
- Lines 592-594 in `conversion_finished()`

Makes it annoying to change colors later.

## What to change

### Step 1: Add colors as class variables
After line 255 (where the class starts), add:

```python
class PDFConverterApp(QMainWindow):
    """Main application window for PDF conversion"""

    # Colors used in the UI
    COLOR_BACKGROUND = "#f8f9fa"
    COLOR_WIDGET_BG = "#e9ecef"
    COLOR_BORDER = "#ced4da"
    COLOR_PRIMARY = "#007bff"
    COLOR_PRIMARY_HOVER = "#0056b3"
    COLOR_TEXT = "#212529"
    COLOR_TEXT_SECONDARY = "#6c757d"
    COLOR_SUCCESS = "#28a745"
    COLOR_ERROR = "#dc3545"
    COLOR_INFO = "#17a2b8"

    def __init__(self):
        # ... rest of code
```

Test: Launch the app, make sure it opens.

### Step 2: Update the stylesheet
In `_init_ui()`, delete lines 275-284 (the local color variables).

Change all the colors in the stylesheet to use `self.COLOR_whatever` instead:

```python
self.setStyleSheet(f"""
    QMainWindow {{
        background-color: {self.COLOR_BACKGROUND};
    }}
    QWidget {{
        color: {self.COLOR_TEXT};
    }}
    # ... etc for rest of stylesheet
""")
```

Test: Launch app, check that colors look the same.

### Step 3: Fix convert_to_pdf method
Line 548 - delete the `COLOR_INFO = "#17a2b8"` line.

Change line 555 to:
```python
self.status_label.setStyleSheet(f"color: {self.COLOR_INFO};")
```

Test: Click convert, status should turn blue.

### Step 4: Fix conversion_finished method
Lines 592-594 - delete those 3 color definitions.

Change lines 598 and 620 to use `self.COLOR_SUCCESS` and `self.COLOR_ERROR` instead.

Test: Finish a conversion, check status turns green or red.

### Step 5: Remove duplicate window setup
Lines 266-267 set the window title twice. Delete those two lines:
```python
self.setWindowTitle("FileConvert - Professional PDF Creator")  # delete
self.setGeometry(100, 100, 650, 550)  # delete
```

Keep the ones in `_init_ui()` method (lines 271-272).

## Quick test checklist

- [ ] App launches
- [ ] Window is the right size
- [ ] Convert button is blue
- [ ] Status turns blue when converting
- [ ] Status turns green on success
- [ ] Status turns red on error

That's it. Now if you want to change colors later, just edit one place.
