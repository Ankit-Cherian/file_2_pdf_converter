# Task 5: Break Up the Long UI Method

**Time:** 2-3 hours
**Difficulty:** Medium
**File:** `file_convert/src/app.py`

## Problem

The `_init_ui()` method is 200+ lines long. Hard to find stuff and make changes.

## What to change

Break it into smaller pieces - one method for each section of the UI.

### Step 1: Make window setup method

Add this before `_init_ui()`:

```python
def _setup_window(self):
    """Setup window title, size, and styles"""
    self.setWindowTitle("File2PDF: Multi-File Converter")
    self.setGeometry(100, 100, 650, 550)

    # Copy all the stylesheet code from _init_ui here
    # Lines 286-375 in current code
    self.setStyleSheet(f"""
        # ... all the style rules ...
    """)
```

### Step 2: Make title method

```python
def _add_title(self, layout):
    """Add the title at the top"""
    title_label = QLabel("File2PDF: Multi-File Converter")
    title_label.setObjectName("TitleLabel")
    title_label.setAlignment(Qt.AlignCenter)
    layout.addWidget(title_label)
```

### Step 3: Make file selection method

```python
def _add_file_section(self, layout):
    """Add the file list and buttons"""
    # File frame
    files_frame = QFrame()
    files_frame.setObjectName("FilesFrame")
    files_layout = QVBoxLayout(files_frame)

    # Header with buttons
    files_header = QHBoxLayout()
    self.file_count_label = QLabel("Selected files: 0")
    files_header.addWidget(self.file_count_label)

    self.browse_button = QPushButton("Add Files...")
    self.browse_button.clicked.connect(self.browse_files)
    files_header.addWidget(self.browse_button)

    clear_button = QPushButton("Clear All")
    clear_button.clicked.connect(self.clear_files)
    files_header.addWidget(clear_button)

    files_layout.addLayout(files_header)

    # File list
    self.file_list = QListWidget()
    self.file_list.setMinimumHeight(120)
    files_layout.addWidget(self.file_list)

    layout.addWidget(files_frame)
```

### Step 4: Make output folder method

```python
def _add_output_section(self, layout):
    """Add output folder selection"""
    output_layout = QHBoxLayout()
    output_layout.setSpacing(10)

    self.output_label = QLabel("Output folder: Default (same as first input)")
    self.output_label.setObjectName("OutputLabel")
    output_layout.addWidget(self.output_label, 7)

    self.output_button = QPushButton("Choose Folder...")
    self.output_button.clicked.connect(self.choose_output_folder)
    output_layout.addWidget(self.output_button, 3)

    layout.addLayout(output_layout)
```

### Step 5: Make progress section method

```python
def _add_progress_section(self, layout):
    """Add progress bar"""
    self.progress_bar = QProgressBar()
    self.progress_bar.setRange(0, 100)
    self.progress_bar.setValue(0)
    self.progress_bar.setTextVisible(True)
    layout.addWidget(self.progress_bar)

    self.current_file_label = QLabel("")
    self.current_file_label.setAlignment(Qt.AlignCenter)
    layout.addWidget(self.current_file_label)
```

### Step 6: Make supported types method

```python
def _add_info_section(self, layout):
    """Add supported file types info"""
    supported_label = QLabel("Supported file types:")
    supported_label.setObjectName("SupportedLabel")

    supported_types = QLabel(
        "Documents: .doc, .docx, .odt, .txt, .md\n"
        "Presentations: .ppt, .pptx, .odp\n"
        "Spreadsheets: .xls, .xlsx, .ods\n"
        "Images: .jpg, .png, .bmp, .gif\n"
        "Others: .html, .csv"
    )
    supported_types.setObjectName("SupportedTypes")

    layout.addWidget(supported_label)
    layout.addWidget(supported_types)
    layout.addStretch(1)
```

### Step 7: Make convert button method

```python
def _add_controls(self, layout):
    """Add convert button and status"""
    self.convert_button = QPushButton("Convert All to PDF")
    self.convert_button.setObjectName("ConvertButton")
    self.convert_button.clicked.connect(self.convert_to_pdf)
    self.convert_button.setEnabled(False)
    layout.addWidget(self.convert_button)

    self.status_label = QLabel("")
    self.status_label.setObjectName("StatusLabel")
    self.status_label.setAlignment(Qt.AlignCenter)
    layout.addWidget(self.status_label)
```

### Step 8: Replace _init_ui with simple version

Now make `_init_ui()` just call all these methods:

```python
def _init_ui(self):
    """Setup the UI"""
    self._setup_window()

    central_widget = QWidget()
    self.setCentralWidget(central_widget)

    main_layout = QVBoxLayout(central_widget)
    main_layout.setContentsMargins(25, 25, 25, 25)
    main_layout.setSpacing(15)

    # Add all the sections
    self._add_title(main_layout)
    self._add_file_section(main_layout)
    self._add_output_section(main_layout)
    self._add_progress_section(main_layout)
    self._add_info_section(main_layout)
    self._add_controls(main_layout)
```

Way easier to read!

## Test checklist

- [ ] App launches
- [ ] Everything looks the same
- [ ] All buttons work
- [ ] File list works
- [ ] Progress bar works
- [ ] Convert works

Now it's way easier to modify specific parts of the UI!
