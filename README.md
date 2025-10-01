# Timestamp Adjuster

A Python application for adjusting timestamps in transcript files. Supports timestamps in `[HH:MM:SS]` format and can add or subtract a specified number of seconds from all timestamps in a file.

## Features

- Adjusts timestamps in `[HH:MM:SS]` format
- Supports both positive (add time) and negative (subtract time) adjustments
- **Auto-generates output filenames** in `outputs/` folder when no output file is specified
- **Organized file management** with dedicated `inputs/` and `outputs/` folders
- **Git-friendly structure** with proper .gitignore configuration
- Can specify custom output file location if needed
- Handles edge cases (negative timestamps become `[00:00:00]`)
- Command-line interface with helpful examples

## Setup

1. Create and activate virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On macOS/Linux
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Command Line Interface

```bash
# Add 3 seconds - creates outputs/transcript_plus_3s.txt
python main.py inputs/transcript.txt 3

# Subtract 5 seconds - creates outputs/transcript_minus_5s.txt  
python main.py inputs/transcript.txt -5

# Adjust timestamps and save to a specific file
python main.py inputs/transcript.txt 10 -o custom_output.txt

# Show help and examples
python main.py
```

### File Organization

- **`inputs/`** - Place your original transcript files here
- **`outputs/`** - Adjusted files are automatically saved here (when no custom output specified)
- **Git Integration** - Input and output files are ignored by git, but folder structure is preserved

### Output File Naming

When no output file is specified (`-o` option), the tool automatically:
- Creates an `outputs/` folder if it doesn't exist
- Generates descriptive filenames:
  - `transcript.txt` + 3 seconds → `outputs/transcript_plus_3s.txt`
  - `transcript.txt` - 5 seconds → `outputs/transcript_minus_5s.txt`
  - `my_file.txt` + 10 seconds → `outputs/my_file_plus_10s.txt`

### Using the Start Script

The start script will run the application in interactive mode:
```bash
./start.sh
```

## Examples

**Input file (inputs/transcript.txt):**
```
[00:03:32] Hello world
[00:03:35] This is a test
[00:04:00] End of transcript
```

**After running `python main.py inputs/transcript.txt 3`:**
Output file: `outputs/transcript_plus_3s.txt`
```
[00:03:35] Hello world
[00:03:38] This is a test
[00:04:03] End of transcript
```

**After running `python main.py inputs/transcript.txt -10`:**
Output file: `outputs/transcript_minus_10s.txt`
```
[00:03:22] Hello world
[00:03:25] This is a test
[00:03:50] End of transcript
```

## Project Structure

```
timestamp_adjuster/
├── .github/
│   └── copilot-instructions.md
├── inputs/                  # Place input transcript files here
│   ├── .gitkeep            # Ensures folder is tracked by git
│   └── transcript.txt      # Example input file
├── outputs/                 # Auto-generated output files
│   ├── .gitkeep            # Ensures folder is tracked by git
│   ├── transcript_plus_3s.txt
│   └── transcript_minus_5s.txt
├── venv/                    # Virtual environment
├── .gitignore              # Git ignore configuration
├── main.py                 # Main application
├── requirements.txt        # Dependencies
├── start.sh                # Start script
└── README.md              # Documentation
```

### Git Configuration

The `.gitignore` file is configured to:
- ✅ **Track folder structure** (inputs/ and outputs/ folders are preserved)
- ❌ **Ignore content files** (transcript files in inputs/ and outputs/ are not committed)
- ❌ **Ignore Python artifacts** (__pycache__, .pyc files, etc.)
- ❌ **Ignore virtual environment** (venv/ folder)
- ❌ **Ignore IDE and OS files** (.vscode/, .DS_Store, etc.)

## Development

The project includes:
- Virtual environment setup
- Start script for easy execution
- Basic project structure

## Project Structure

```
timestamp_adjuster/
├── .github/
│   └── copilot-instructions.md
├── venv/                    # Virtual environment (created after setup)
├── main.py                  # Main application entry point
├── requirements.txt         # Python dependencies
├── start.sh                 # Start script
└── README.md               # This file
```
