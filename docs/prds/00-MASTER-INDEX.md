# Code Optimization Tasks

Just some cleanup ideas to make the code easier to work with. Each task can be done independently.

## Task List

| Task | What it does | Time | Difficulty |
|------|-------------|------|-----------|
| Task 1 | Move repeated color codes to one place | 1-2 hrs | Easy |
| Task 2 | Simplify LibreOffice path finding | 2-3 hrs | Medium |
| Task 3 | Better file type handling system | 3-4 hrs | Medium |
| Task 4 | Clean up progress reporting | 1-2 hrs | Easy |
| Task 5 | Break up the long UI method | 2-3 hrs | Medium |
| Task 6 | Remove unused code and fix small stuff | 1 hr | Easy |

## Order to do them

**Easy wins first** (can do together):
- Task 1: Color constants
- Task 6: Code cleanup

**Backend stuff** (can do together):
- Task 2: LibreOffice path
- Task 4: Progress reporting

**Core changes**:
- Task 3: File type handlers

**UI work** (do after others):
- Task 5: Split up UI code

## Testing

For all changes, make sure:
- App still launches
- Files still convert
- Progress bar works
- Error messages show up
- Nothing looks different to users

Check the individual task files for details on what to change.
