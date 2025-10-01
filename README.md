# Timestamp Adjuster

A Python application for adjusting timestamps in transcript files. Supports **configurable timestamp formats** via YAML configuration and can add or subtract a specified number of seconds from all timestamps in a file.

## Features

- **Interactive CLI mode** - User-friendly file selection and adjustment input
- **Configurable timestamp formats** via YAML configuration
- Multiple input formats: `[HH:MM:SS]`, `HH:MM:SS`, `[H:MM:SS]`, etc.
- **Customizable output format** with template strings
- **Auto-generates output filenames** with descriptive names
- **Priority-based configuration**: CLI args → Environment vars → Config file → Defaults
- Handles edge cases (negative timestamps become `[00:00:00]`)

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

### Interactive Mode (Recommended)

The easiest way to use the Timestamp Adjuster is through the interactive mode:

```bash
# Quick start with provided script
./start.sh

# Or manually activate environment and run
source venv/bin/activate
python main.py
```

The interactive mode will:
1. Show available files in the `inputs/` folder
2. Let you select a file from a numbered menu
3. Display a preview of the file content (optional)
4. Ask for time adjustment in seconds
5. Process the file and save to `outputs/` folder

### Command Line Mode

For automation or scripting, use the traditional command-line interface:

```bash
# Basic usage
python main.py inputs/transcript.txt 3

# Interactive mode (explicit flag)
python main.py -i

# Custom output format
python main.py inputs/transcript.txt -5 -f "({hours:02d}:{minutes:02d}:{seconds:02d})"

# Custom output file
python main.py inputs/transcript.txt 15 -o custom_output.txt

# Show help
python main.py --help
```

## Configuration

### Priority System
1. **CLI arguments** (highest priority) - `-f`, `-o`, `-c` options
2. **Environment variables** - `TIMESTAMP_FORMAT`, etc.
3. **Configuration file** - `config.yaml` (automatically detected)
4. **Built-in defaults** (lowest priority)

### Setup Configuration
```bash
# Copy the sample configuration
cp config.sample.yaml config.yaml

# Edit config.yaml to customize settings
```

### Environment Variables
```bash
export TIMESTAMP_FORMAT="({hours:02d}:{minutes:02d}:{seconds:02d})"
export TIMESTAMP_INPUT_DIR="my_inputs"
export TIMESTAMP_OUTPUT_DIR="my_outputs"
```

## Examples

### Interactive Mode Example

Running the interactive mode (recommended for beginners):

```bash
./start.sh
```

**Sample interactive session:**
```
🕐 Timestamp Adjuster - Interactive Mode
=============================================
Welcome! This tool helps you adjust timestamps in transcript files.
Let's get started by selecting a file and adjustment amount.

📁 Available files in inputs folder:
========================================
  1. transcript.txt (24.7 KB)

Select a file (1-1) or 'q' to quit: 1

✅ Selected file: transcript.txt
Would you like to see a preview of the file? (y/n): y

📄 Preview of transcript.txt (first 10 lines):
--------------------------------------------------
   1: [00:03:32] Hello world
   2: [00:03:35] This is a test
   3: [00:04:00] End of transcript

⏰ Time Adjustment
====================
Enter the number of seconds to adjust timestamps:
  • Positive numbers (e.g., 30) to add time
  • Negative numbers (e.g., -15) to subtract time
  • 0 to make no adjustment

Adjustment in seconds (or 'q' to quit): 20
✅ Will ADD 20 seconds to all timestamps.
Proceed? (y/n): y

🔄 Processing transcript.txt...
Successfully adjusted timestamps by 20 seconds.
Output written to: outputs/transcript_plus20s.txt
✅ File processed successfully!
```

### Basic Usage

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

### Custom Format Examples

**Using parentheses format:**
```bash
python main.py inputs/transcript.txt 5 -f "({hours:02d}:{minutes:02d}:{seconds:02d})"
```
Output:
```
(00:03:37) Hello world
(00:03:40) This is a test
(00:04:05) End of transcript
```

**No brackets format:**
```bash
python main.py inputs/transcript.txt 2 -f "{hours:02d}:{minutes:02d}:{seconds:02d}"
```
Output:
```
00:03:34 Hello world
00:03:37 This is a test
00:04:02 End of transcript
```

### Supported Input Formats

The tool automatically detects and processes these timestamp formats:
- `[HH:MM:SS]` - Standard bracketed format
- `HH:MM:SS` - Simple colon-separated format  
- `[H:MM:SS]` - Flexible hour format
- Custom formats can be added via configuration

Each format can be enabled/disabled in `config.yaml`:
```yaml
input_formats:
  - pattern: '\[(\d{2}):(\d{2}):(\d{2})\]'
    name: "bracketed_hms"
    groups: ["hours", "minutes", "seconds"]
    enabled: true    # Set to false to disable this format
```

## Project Structure

```
timestamp_adjuster/
├── inputs/                  # Input transcript files
├── outputs/                 # Generated output files
├── tests/                   # Unit test modules
│   ├── __init__.py
│   ├── test_parsing.py      # Timestamp parsing tests
│   ├── test_formatting.py   # Timestamp formatting tests
│   ├── test_adjustment.py   # Timestamp adjustment tests
│   ├── test_config.py       # Configuration management tests
│   ├── test_file_processing.py # File processing tests
│   └── test_integration.py  # End-to-end integration tests
├── config.py               # Configuration management
├── config.yaml             # User config file
├── config.sample.yaml      # Sample configuration
├── main.py                 # Main application
├── start.sh                # Quick start script (activates venv and runs app)
├── run_tests.sh            # Test runner script
└── requirements.txt        # Dependencies (PyYAML)
```

## Testing

Run the comprehensive unit test suite:

```bash
# Run all tests
./run_tests.sh

# Or run specific test modules
source venv/bin/activate
python -m unittest tests.test_parsing -v          # Test timestamp parsing
python -m unittest tests.test_formatting -v       # Test timestamp formatting  
python -m unittest tests.test_adjustment -v       # Test timestamp adjustment
python -m unittest tests.test_config -v           # Test configuration management
python -m unittest tests.test_file_processing -v  # Test file processing
python -m unittest tests.test_integration -v      # Test end-to-end integration
```

## Test Coverage

The test suite is organized into separate modules in the `/tests` directory:

- 🧪 **test_parsing.py** - Timestamp parsing for all supported formats
- 🧪 **test_formatting.py** - Timestamp formatting with various output templates  
- 🧪 **test_adjustment.py** - Timestamp adjustment logic (positive/negative)
- 🧪 **test_config.py** - Configuration management and enabled/disabled formats
- 🧪 **test_file_processing.py** - File processing with auto-generated and custom output filenames
- 🧪 **test_integration.py** - End-to-end integration testing

**Total Coverage:** 26 comprehensive unit tests covering all functionality and edge cases.

