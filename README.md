# notepad## Simple Notepad — Minimal Win32 Text Editor (C89)

Simple Notepad is a compact, single-file C program implementing a minimal Notepad-like text editor using the Win32 API. It provides New/Open/Save file operations, basic Find and Replace (single occurrence), a multiline edit control with scrollbars, and a simple custom modal input prompt. The source is ANSI C compatible with C89 and released under the GNU General Public License v3.0. Repository: https://github.com/wangyifan349/notepad

## Features
- Single-source-file implementation using Win32 API.  
- File: New, Open, Save, Exit. Edit: Find (Ctrl+F), Replace (Ctrl+H). Help: About. (Note: keyboard accelerators are shown in menu text but no accelerator table is implemented.)  
- Multiline EDIT control with vertical and horizontal scrollbars; resizes with window.  
- File I/O via CreateFile/ReadFile/WriteFile; current filename stored in g_filename and shown in window title after open/save.  
- Simple modal string input implemented by creating a small window with STATIC/EDIT/BUTTON controls (PromptString).  
- Find uses strstr to locate the first occurrence and selects it (EM_SETSEL); Replace replaces the first occurrence by reconstructing the text buffer.  
- Compact, easy to read, portable across common Windows C toolchains (MinGW, MSVC).

## Build
Prerequisites: Windows development environment with Win32 SDK headers/libs. Example commands: MinGW: gcc -o simple_notepad.exe notepad.c -mwindows. MSVC (Developer Command Prompt): cl /O2 notepad.c user32.lib gdi32.lib kernel32.lib comdlg32.lib

## Usage
Run the executable; use the File menu to create/open/save; Edit→Find (Ctrl+F) searches for a substring; Edit→Replace (Ctrl+H) replaces the first match; About shows program info. The window title updates to "path - 简易记事本" after opening or saving.

## Implementation details
- Entry: WinMain registers a WNDCLASSEX and creates the main window titled "简易记事本". Menu created with CreateMenu/AppendMenu. Main control is a child EDIT created in WM_CREATE; EM_LIMITTEXT used to allow large text. WM_SIZE resizes the edit control.  
- File operations: DoFileOpen uses GetOpenFileName, CreateFile, GetFileSize, ReadFile; DoFileSave uses GetSaveFileName when no current filename, CreateFile with CREATE_ALWAYS and WriteFile. Buffers allocated with malloc/free; file contents are treated as raw bytes (no BOM/encoding handling).  
- Dialogs: PromptString creates a simple modal input window and runs a manual GetMessage loop to capture OK/Cancel. DoFind and DoReplace call PromptString, fetch the full edit text via GetWindowText, operate on it, then set selection or replace the edit text.  
- Memory and limits: The program reads entire files into memory and allocates temporary buffers for edits; very large files may exhaust memory. No streaming or chunked I/O.  
- Error handling: Basic MessageBox notifications for I/O and allocation failures.  
- Localization: UI strings are in Chinese in the source; change literals to English or use resources for localization.  
- Threading: Single-threaded UI; file I/O runs on the UI thread.

## Limitations and recommended improvements
- Encoding: No explicit Unicode handling—source uses ANSI APIs and treats files as byte streams. To support Unicode robustly, port to wide-character APIs (CreateWindowW/GetWindowTextW/etc.), handle BOMs, or perform UTF-8↔UTF-16 conversions.  
- Replace and Find: Only first occurrence handled; no options for case sensitivity, whole-word, or regex searches; no Replace All.  
- Shortcuts: Menu labels show shortcuts but no accelerator table is implemented—add an accelerator table or handle WM_KEYDOWN/TranslateAccelerator for proper shortcuts.  
- Dialogs: PromptString uses a custom lightweight modal loop; consider using DialogBoxParam with dialog templates for standard modal behavior.  
- Large-file performance: For large files, consider streaming, memory-mapped files, or incremental editing to avoid large allocations.  
- Undo/Redo, status bar, recent files, Save As, and other UX features are not implemented.

## License
This project is licensed under the GNU General Public License v3.0. Include a LICENSE file with the GPLv3 text and add a license header to source files, for example:  
/* Simple Notepad — Minimal Win32 Text Editor (C89) Copyright (C) <year> <Your Name> This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. See LICENSE for full text. */

## Contributing
Fork, implement focused changes, add build instructions and tests, and submit pull requests. Prefer small commits; document new behavior and include any additional dependencies.

## Contact
Repository: https://github.com/wangyifan349/notepad. Replace author/contact details in README or source as desired.
