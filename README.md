# VAT Calculator Pro

A professional desktop application for calculating VAT (Value Added Tax) with advanced features including data persistence, report generation, and calculation history management.

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.7+-green)
![License](https://img.shields.io/badge/license-MIT-orange)

## 📋 Table of Contents

- [Features](#features)
- [Screenshots](#screenshots)
- [Installation](#installation)
- [Usage](#usage)
- [Building Executable](#building-executable)
- [Database](#database)
- [Export Options](#export-options)
- [System Requirements](#system-requirements)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

## ✨ Features

### Core Functionality
- **Dynamic VAT Calculation**: Calculate VAT-inclusive and VAT-exclusive prices in real-time
- **Customizable VAT Rate**: Set any VAT rate percentage (default: 20%)
- **Multi-row Support**: Add unlimited rows for batch calculations
- **Automatic Totals**: Real-time calculation of total amounts

### Data Management
- **Save Calculations**: Store calculations with custom names for future reference
- **Calculation History**: Browse and reload previously saved calculations
- **Database Backup/Restore**: Protect your data with backup and restore functionality
- **SQLite Database**: Lightweight, file-based database for data persistence

### Reporting
- **CSV Export**: Export calculations to CSV format for spreadsheet applications
- **HTML Reports**: Generate professional HTML reports with styling
- **Report Generation**: Create reports from saved calculations

### User Interface
- **Modern Design**: Clean, professional interface with gradient styling
- **Splash Screen**: Animated loading screen with progress indicator
- **Tabbed Interface**: Separate tabs for calculator and saved calculations
- **Scrollable Canvas**: Handle large datasets with smooth scrolling
- **Responsive Layout**: Minimum window size with expandable interface

## 🖼️ Screenshots

### Main Calculator Interface
The main calculator features a spreadsheet-like interface with:
- Item description column
- Price including VAT input
- Automatically calculated price excluding VAT
- VAT amount display
- Running totals at the bottom

### Saved Calculations
Browse, load, and manage your calculation history with:
- Calculation name and date
- VAT rate used
- Quick load functionality
- Delete and report generation options

## 🚀 Installation

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Required Libraries
```bash
pip install tkinter
```

**Note**: `tkinter` usually comes pre-installed with Python. If not available, install it using your system's package manager.

### Clone or Download
```bash
# Clone the repository (if using git)
git clone <repository-url>
cd "VAT Calculator"

# Or simply download and extract the project files
```

## 💻 Usage

### Running the Application

#### From Source
```bash
python vat_calculator_pro.py
```

#### From Executable
Double-click the `VAT Calculator Pro.exe` file in the `dist` folder.

### Basic Workflow

1. **Set VAT Rate**: Enter your desired VAT rate percentage (e.g., 20 for 20%)

2. **Enter Data**:
   - Type item descriptions in the "Item" column
   - Enter prices including VAT in the "Price Inc. VAT" column
   - Watch as the calculator automatically computes:
     - Price excluding VAT
     - VAT amount

3. **Add/Remove Rows**:
   - Click "+ Row" to add more items
   - Click "- Row" to remove the last row
   - Use the "+ Add Row" button in the table

4. **Save Calculation**:
   - Enter a name in the "Name" field
   - Click "Save Calculation"
   - Access saved calculations in the "Saved Calculations" tab

5. **Export Reports**:
   - Go to File → Export to CSV
   - Or File → Export to HTML Report
   - Choose your save location

### Keyboard Shortcuts
- **Tab**: Navigate between fields
- **Enter**: Move to next row (when in input field)
- **Mouse Wheel**: Scroll through calculations

## 🔨 Building Executable

The project includes PyInstaller spec files for creating standalone executables.

### Build Command
```bash
# Using the spec file
pyinstaller "VAT Calculator Pro.spec"

# Or manual build
pyinstaller --name "VAT Calculator Pro" --windowed --onefile vat_calculator_pro.py
```

### Spec File Options
The included `.spec` files configure:
- Application name and icon
- Single-file executable
- Windows mode (no console)
- Data file inclusion
- Build and distribution directories

### Output
The executable will be created in the `dist` folder:
```
dist/
└── VAT Calculator Pro.exe
```

## 🗄️ Database

### Database Structure
The application uses SQLite with the following schema:

```sql
CREATE TABLE calculations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    created_at TEXT,
    vat_rate REAL,
    data TEXT
);
```

### Database Location
- **Default**: `vat_calculator.db` in the application directory
- **Portable**: The database file can be moved with the application

### Backup & Restore
- **Backup**: File → Backup Database (saves as `.sql` file)
- **Restore**: File → Restore Database (loads from `.sql` file)

## 📊 Export Options

### CSV Export
- Includes all calculation data
- Compatible with Excel, Google Sheets, etc.
- Contains:
  - Header with generation date and VAT rate
  - Item-by-item breakdown
  - Total calculations

### HTML Report
Professional HTML reports with:
- Modern styling and gradients
- Responsive table layout
- Summary section
- Print-friendly format
- Embedded CSS (no external dependencies)

## 💾 System Requirements

### Minimum Requirements
- **OS**: Windows 7/8/10/11, macOS 10.12+, Linux (most distributions)
- **RAM**: 256 MB
- **Storage**: 50 MB free space
- **Display**: 1024x768 resolution

### Recommended
- **OS**: Windows 10/11
- **RAM**: 512 MB or more
- **Display**: 1920x1080 or higher

## 📁 Project Structure

```
VAT Calculator/
├── vat_calculator.py           # Basic version
├── vat_calculator_enhanced.py  # Enhanced version
├── vat_calculator_pro.py       # Professional version (main)
├── VAT Calculator.spec         # PyInstaller spec (basic)
├── VAT Calculator Pro.spec     # PyInstaller spec (pro)
├── vat_calculator.db          # SQLite database (created on first run)
├── README.md                  # This file
├── build/                     # Build artifacts (generated)
├── dist/                      # Distribution folder (generated)
│   └── VAT Calculator Pro.exe
└── __pycache__/              # Python cache (generated)
```

## 🎨 Customization

### Changing Default VAT Rate
Edit line 258 in `vat_calculator_pro.py`:
```python
self.current_vat_rate = tk.StringVar(value="20")  # Change "20" to your default
```

### Modifying Colors
The application uses a consistent color scheme:
- **Primary**: `#1a1a2e` (Dark blue)
- **Accent**: `#00d9ff` (Cyan)
- **Background**: `#f0f2f5` (Light gray)

Edit the `setup_styles()` and widget creation methods to customize.

### Currency Symbol
Currently set to GBP (£). To change:
1. Search for `£` in the code
2. Replace with your currency symbol (e.g., `$`, `€`, `₹`)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see below for details:

```
MIT License

Copyright (c) 2026 VAT Calculator Pro

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## 🐛 Known Issues

- None currently reported

## 📞 Support

For issues, questions, or suggestions:
- Create an issue in the repository
- Contact the development team

## 🔄 Version History

### Version 1.0.0 (Current)
- Initial release
- Core VAT calculation functionality
- Database persistence
- CSV and HTML export
- Backup and restore features
- Professional UI with splash screen

---

**Project by - Randika Nawarathne**
**Powered by - Rough X Developers </>**
