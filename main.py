#!/usr/bin/env python3
"""
Timestamp Adjuster - Adjusts timestamps in transcript files.
Supports configurable timestamp formats via YAML configuration.
"""

import re
import argparse
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any

from config import get_config


def parse_timestamp(timestamp_str, formats: List[Dict[str, Any]]) -> Optional[int]:
    """
    Parse a timestamp string using configured formats and return total seconds.
    
    Args:
        timestamp_str (str): Timestamp string
        formats (List[Dict]): List of format configurations
        
    Returns:
        Optional[int]: Total seconds if parsed successfully, None otherwise
    """
    for fmt in formats:
        # Skip disabled formats
        if not fmt.get("enabled", True):
            continue
            
        pattern = fmt["pattern"]
        groups = fmt["groups"]
        
        match = re.search(pattern, timestamp_str)
        if match:
            # Extract time components based on group names
            time_parts = {}
            for i, group_name in enumerate(groups, 1):
                time_parts[group_name] = int(match.group(i))
            
            # Calculate total seconds
            hours = time_parts.get("hours", 0)
            minutes = time_parts.get("minutes", 0) 
            seconds = time_parts.get("seconds", 0)
            
            return hours * 3600 + minutes * 60 + seconds
    
    return None


def seconds_to_timestamp(total_seconds: int, output_format: str) -> str:
    """
    Convert total seconds to timestamp using configured output format.
    
    Args:
        total_seconds (int): Total seconds
        output_format (str): Format template string
        
    Returns:
        str: Formatted timestamp
    """
    # Handle negative timestamps by setting them to 00:00:00
    if total_seconds < 0:
        total_seconds = 0
        
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    
    return output_format.format(
        hours=hours,
        minutes=minutes, 
        seconds=seconds
    )


def adjust_timestamps(content: str, adjustment_seconds: int, config) -> str:
    """
    Adjust all timestamps in the content by the specified number of seconds.
    
    Args:
        content (str): The transcript content
        adjustment_seconds (int): Number of seconds to adjust (can be negative)
        config: Configuration object
        
    Returns:
        str: Content with adjusted timestamps
    """
    formats = config.get_timestamp_formats()
    output_format = config.get_output_format()
    
    # Create a combined pattern from all input formats
    all_patterns = [fmt["pattern"] for fmt in formats]
    combined_pattern = '|'.join(f'({pattern})' for pattern in all_patterns)
    
    def replace_timestamp(match):
        # Find which pattern matched
        matched_text = match.group(0)
        
        # Parse the matched timestamp
        total_seconds = parse_timestamp(matched_text, formats)
        if total_seconds is None:
            return matched_text  # Return unchanged if parsing failed
        
        # Adjust the timestamp
        new_total_seconds = total_seconds + adjustment_seconds
        
        # Convert back to timestamp format
        return seconds_to_timestamp(new_total_seconds, output_format)
    
    # Replace all timestamps in the content
    adjusted_content = re.sub(combined_pattern, replace_timestamp, content)
    return adjusted_content


def generate_output_filename(input_file: str, adjustment_seconds: int, config) -> Path:
    """
    Generate an output filename based on the input file and adjustment.
    
    Args:
        input_file (str): Path to input file
        adjustment_seconds (int): Number of seconds adjusted
        config: Configuration object
        
    Returns:
        Path: Generated output file path in outputs folder
    """
    input_path = Path(input_file)
    
    # Create outputs directory if it doesn't exist
    outputs_dir = Path(config.get_output_dir())
    outputs_dir.mkdir(exist_ok=True)
    
    # Get the base filename without extension
    base_name = input_path.stem
    extension = input_path.suffix
    
    # Generate sign and template variables
    if adjustment_seconds >= 0:
        sign = config.get_positive_sign()
    else:
        sign = config.get_negative_sign()
    
    # Format filename using template
    template = config.get_output_template()
    output_filename = template.format(
        basename=base_name,
        extension=extension,
        adjustment=abs(adjustment_seconds),
        sign=sign
    )
    
    output_path = outputs_dir / output_filename
    return output_path


def process_file(input_file: str, output_file: Optional[str], adjustment_seconds: int, config) -> bool:
    """
    Process a transcript file and adjust all timestamps.
    
    Args:
        input_file (str): Path to input transcript file
        output_file (Optional[str]): Path to output file (if None, auto-generates in outputs folder)
        adjustment_seconds (int): Number of seconds to adjust
        config: Configuration object
    """
    input_path = Path(input_file)
    
    if not input_path.exists():
        print(f"Error: Input file '{input_file}' not found.")
        return False
    
    try:
        # Read the input file
        encoding = config.get_encoding()
        with open(input_path, 'r', encoding=encoding) as f:
            content = f.read()
        
        # Adjust timestamps
        adjusted_content = adjust_timestamps(content, adjustment_seconds, config)
        
        # Determine output file
        if output_file is None:
            output_path = generate_output_filename(input_file, adjustment_seconds, config)
        else:
            output_path = Path(output_file)
        
        # Create output directory if it doesn't exist
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write the adjusted content
        with open(output_path, 'w', encoding=encoding) as f:
            f.write(adjusted_content)
        
        print(f"Successfully adjusted timestamps by {adjustment_seconds} seconds.")
        print(f"Output written to: {output_path}")
        return True
        
    except Exception as e:
        print(f"Error processing file: {e}")
        return False


def list_input_files() -> List[Path]:
    """
    List all files in the inputs directory (excluding test files and directories).
    
    Returns:
        List[Path]: List of available input files
    """
    inputs_dir = Path("inputs")
    if not inputs_dir.exists():
        return []
    
    # Get all files, excluding test files and python files
    files = []
    for file_path in inputs_dir.iterdir():
        if (file_path.is_file() and 
            not file_path.name.startswith('.') and 
            not file_path.name.startswith('test_') and
            not file_path.name.endswith('.py')):
            files.append(file_path)
    
    return sorted(files)


def display_file_menu(files: List[Path]) -> None:
    """Display a numbered menu of available files."""
    print("\n📁 Available files in inputs folder:")
    print("=" * 40)
    
    if not files:
        print("No files found in inputs folder.")
        return
    
    for i, file_path in enumerate(files, 1):
        file_size = file_path.stat().st_size
        size_str = f"{file_size:,} bytes" if file_size < 1024 else f"{file_size/1024:.1f} KB"
        print(f"  {i}. {file_path.name} ({size_str})")


def get_user_file_selection(files: List[Path]) -> Optional[Path]:
    """
    Get user's file selection from the menu.
    
    Args:
        files (List[Path]): List of available files
        
    Returns:
        Optional[Path]: Selected file path or None if cancelled
    """
    if not files:
        return None
    
    while True:
        try:
            choice = input(f"\nSelect a file (1-{len(files)}) or 'q' to quit: ").strip().lower()
            
            if choice == 'q':
                return None
            
            file_index = int(choice) - 1
            if 0 <= file_index < len(files):
                return files[file_index]
            else:
                print(f"Please enter a number between 1 and {len(files)}.")
                
        except ValueError:
            print("Please enter a valid number or 'q' to quit.")


def get_time_adjustment() -> Optional[int]:
    """
    Get time adjustment from user input.
    
    Returns:
        Optional[int]: Adjustment in seconds or None if cancelled
    """
    print("\n⏰ Time Adjustment")
    print("=" * 20)
    print("Enter the number of seconds to adjust timestamps:")
    print("  • Positive numbers (e.g., 30) to add time")
    print("  • Negative numbers (e.g., -15) to subtract time")
    print("  • 0 to make no adjustment")
    
    while True:
        try:
            adjustment_input = input("\nAdjustment in seconds (or 'q' to quit): ").strip().lower()
            
            if adjustment_input == 'q':
                return None
            
            adjustment = int(adjustment_input)
            
            # Confirm the adjustment
            if adjustment == 0:
                print("⚠️  No adjustment will be made (0 seconds).")
            elif adjustment > 0:
                print(f"✅ Will ADD {adjustment} seconds to all timestamps.")
            else:
                print(f"✅ Will SUBTRACT {abs(adjustment)} seconds from all timestamps.")
            
            confirm = input("Proceed? (y/n): ").strip().lower()
            if confirm in ['y', 'yes']:
                return adjustment
            else:
                print("Let's try again...")
                continue
                
        except ValueError:
            print("Please enter a valid number or 'q' to quit.")


def preview_file_content(file_path: Path, config, max_lines: int = 10) -> None:
    """
    Show a preview of the file content with timestamp highlighting.
    
    Args:
        file_path (Path): File to preview
        config: Configuration object
        max_lines (int): Maximum lines to show
    """
    try:
        encoding = config.get_encoding()
        with open(file_path, 'r', encoding=encoding) as f:
            lines = f.readlines()
        
        print(f"\n📄 Preview of {file_path.name} (first {min(len(lines), max_lines)} lines):")
        print("-" * 50)
        
        formats = config.get_timestamp_formats()
        all_patterns = [fmt["pattern"] for fmt in formats if fmt.get("enabled", True)]
        combined_pattern = '|'.join(f'({pattern})' for pattern in all_patterns)
        
        for i, line in enumerate(lines[:max_lines], 1):
            line = line.rstrip()
            # Highlight timestamps with brackets
            highlighted_line = re.sub(combined_pattern, r'[\033[93m\g<0>\033[0m]', line)
            print(f"  {i:2d}: {highlighted_line}")
        
        if len(lines) > max_lines:
            print(f"  ... ({len(lines) - max_lines} more lines)")
            
    except Exception as e:
        print(f"Error reading file: {e}")


def interactive_mode():
    """Run the application in interactive mode."""
    print("🕐 Timestamp Adjuster - Interactive Mode")
    print("=" * 45)
    print("Welcome! This tool helps you adjust timestamps in transcript files.")
    print("Let's get started by selecting a file and adjustment amount.\n")
    
    # Load configuration
    config = get_config()
    
    while True:
        # List available files
        input_files = list_input_files()
        display_file_menu(input_files)
        
        if not input_files:
            print("\n❌ No files found in the inputs folder.")
            print("Please add some transcript files to the 'inputs' directory and try again.")
            break
        
        # Get file selection
        selected_file = get_user_file_selection(input_files)
        if selected_file is None:
            print("\n👋 Goodbye!")
            break
        
        print(f"\n✅ Selected file: {selected_file.name}")
        
        # Show file preview
        show_preview = input("Would you like to see a preview of the file? (y/n): ").strip().lower()
        if show_preview in ['y', 'yes']:
            preview_file_content(selected_file, config)
        
        # Get time adjustment
        adjustment_seconds = get_time_adjustment()
        if adjustment_seconds is None:
            print("\n👋 Goodbye!")
            break
        
        # Process the file
        print(f"\n🔄 Processing {selected_file.name}...")
        success = process_file(str(selected_file), None, adjustment_seconds, config)
        
        if success:
            print("✅ File processed successfully!")
        else:
            print("❌ Failed to process file.")
        
        # Ask if user wants to process another file
        print("\n" + "=" * 45)
        continue_choice = input("Would you like to process another file? (y/n): ").strip().lower()
        if continue_choice not in ['y', 'yes']:
            print("\n👋 Goodbye!")
            break


def main():
    """Main function to run the timestamp adjuster."""
    parser = argparse.ArgumentParser(
        description="Adjust timestamps in transcript files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                                   # Run in interactive mode
  python main.py inputs/transcript.txt 3          # Creates outputs/transcript_plus_3s.txt
  python main.py inputs/transcript.txt -5         # Creates outputs/transcript_minus_5s.txt
  python main.py inputs/file.txt 10 -o output.txt # Creates output.txt in current directory
        """
    )
    
    parser.add_argument('input_file', nargs='?', help='Input transcript file')
    parser.add_argument('adjustment', nargs='?', type=int, 
                       help='Number of seconds to adjust (positive or negative)')
    parser.add_argument('-o', '--output', dest='output_file',
                       help='Output file (if not specified, auto-generates in outputs/ folder)')
    parser.add_argument('-c', '--config', dest='config_file',
                       help='Configuration file path (default: searches for config.yaml)')
    parser.add_argument('-f', '--format', dest='output_format',
                       help='Override output timestamp format (e.g., "[{hours:02d}:{minutes:02d}:{seconds:02d}]")')
    parser.add_argument('-i', '--interactive', action='store_true',
                       help='Run in interactive mode')
    
    args = parser.parse_args()
    
    # If no arguments provided or interactive flag is set, run interactive mode
    if len(sys.argv) == 1 or args.interactive or (args.input_file is None and args.adjustment is None):
        interactive_mode()
        return
    
    # Validate required arguments for non-interactive mode
    if args.input_file is None or args.adjustment is None:
        print("Error: Both input_file and adjustment are required for non-interactive mode.")
        print("Use 'python main.py --help' for usage information.")
        print("Or run 'python main.py' for interactive mode.")
        sys.exit(1)
    
    # Load configuration
    config = get_config(args.config_file)
    
    # Override output format if specified
    if args.output_format:
        config.config_data["timestamp"]["output_format"] = args.output_format
    
    # Process the file
    success = process_file(args.input_file, args.output_file, args.adjustment, config)
    
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
