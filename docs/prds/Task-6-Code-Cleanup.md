# Task 6: Code Cleanup & Small Fixes

**Time:** ~1 hour
**Difficulty:** Easy
**File:** `file_convert/src/app.py`

## Small things to fix

Just some minor cleanup stuff I noticed:

### 1. Remove unused import

Line 12 - delete this line:
```python
import time  # Not used anywhere
```

### 2. Simplify font code

Lines 123-128 and line 18 - We're trying to register Courier font but it's already built into PDFs.

Delete line 18:
```python
from reportlab.pdfbase.ttfonts import TTFont  # Not needed
```

Replace lines 123-128 with:
```python
# Courier is a standard PDF font
font_name = 'Courier'
```

Test: Convert a text file, should still work fine.

### 3. Fix status indicators

Line 581 uses emoji (✅ and ❌) which might not show up on all computers.

Change to:
```python
status_prefix = "[OK] " if success else "[FAIL] "
```

Test: Convert files, check the list shows [OK] or [FAIL].

## Quick test

- [ ] App launches without errors
- [ ] Convert an image
- [ ] Convert a text file
- [ ] File list shows [OK] / [FAIL]
- [ ] No import errors

That's it - just removing unused stuff and making it more compatible!
