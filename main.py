#!/usr/bin/env python3
"""
Timestamp Adjuster - Adjusts timestamps in transcript files.
Supports timestamps in [HH:MM:SS] format.
"""

import re
import argparse
import sys
from pathlib import Path


def parse_timestamp(timestamp_str):
    """
    Parse a timestamp string in format [HH:MM:SS] and return total seconds.
    
    Args:
        timestamp_str (str): Timestamp in format [HH:MM:SS]
        
    Returns:
        int: Total seconds
    """
    # Remove brackets and split by colon
    time_part = timestamp_str.strip('[]')
    hours, minutes, seconds = map(int, time_part.split(':'))
    return hours * 3600 + minutes * 60 + seconds


def seconds_to_timestamp(total_seconds):
    """
    Convert total seconds back to [HH:MM:SS] format.
    
    Args:
        total_seconds (int): Total seconds
        
    Returns:
        str: Timestamp in format [HH:MM:SS]
    """
    # Handle negative timestamps by setting them to 00:00:00
    if total_seconds < 0:
        total_seconds = 0
        
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    
    return f"[{hours:02d}:{minutes:02d}:{seconds:02d}]"


def adjust_timestamps(content, adjustment_seconds):
    """
    Adjust all timestamps in the content by the specified number of seconds.
    
    Args:
        content (str): The transcript content
        adjustment_seconds (int): Number of seconds to adjust (can be negative)
        
    Returns:
        str: Content with adjusted timestamps
    """
    # Regular expression to find timestamps in format [HH:MM:SS]
    timestamp_pattern = r'\[(\d{2}):(\d{2}):(\d{2})\]'
    
    def replace_timestamp(match):
        # Parse the matched timestamp
        original_timestamp = match.group(0)
        total_seconds = parse_timestamp(original_timestamp)
        
        # Adjust the timestamp
        new_total_seconds = total_seconds + adjustment_seconds
        
        # Convert back to timestamp format
        return seconds_to_timestamp(new_total_seconds)
    
    # Replace all timestamps in the content
    adjusted_content = re.sub(timestamp_pattern, replace_timestamp, content)
    return adjusted_content


def generate_output_filename(input_file, adjustment_seconds):
    """
    Generate an output filename based on the input file and adjustment.
    
    Args:
        input_file (str): Path to input file
        adjustment_seconds (int): Number of seconds adjusted
        
    Returns:
        Path: Generated output file path in outputs folder
    """
    input_path = Path(input_file)
    
    # Create outputs directory if it doesn't exist
    outputs_dir = Path("outputs")
    outputs_dir.mkdir(exist_ok=True)
    
    # Get the base filename without extension
    base_name = input_path.stem
    extension = input_path.suffix
    
    # Generate suffix based on adjustment
    if adjustment_seconds >= 0:
        suffix = f"_plus_{adjustment_seconds}s"
    else:
        suffix = f"_minus_{abs(adjustment_seconds)}s"
    
    # Construct the output filename
    output_filename = f"{base_name}{suffix}{extension}"
    output_path = outputs_dir / output_filename
    
    return output_path


def process_file(input_file, output_file, adjustment_seconds):
    """
    Process a transcript file and adjust all timestamps.
    
    Args:
        input_file (str): Path to input transcript file
        output_file (str): Path to output file (if None, auto-generates in outputs folder)
        adjustment_seconds (int): Number of seconds to adjust
    """
    input_path = Path(input_file)
    
    if not input_path.exists():
        print(f"Error: Input file '{input_file}' not found.")
        return False
    
    try:
        # Read the input file
        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Adjust timestamps
        adjusted_content = adjust_timestamps(content, adjustment_seconds)
        
        # Determine output file
        if output_file is None:
            output_path = generate_output_filename(input_file, adjustment_seconds)
        else:
            output_path = Path(output_file)
        
        # Create output directory if it doesn't exist
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write the adjusted content
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(adjusted_content)
        
        print(f"Successfully adjusted timestamps by {adjustment_seconds} seconds.")
        print(f"Output written to: {output_path}")
        return True
        
    except Exception as e:
        print(f"Error processing file: {e}")
        return False


def main():
    """Main function to run the timestamp adjuster."""
    parser = argparse.ArgumentParser(
        description="Adjust timestamps in transcript files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py inputs/transcript.txt 3          # Creates outputs/transcript_plus_3s.txt
  python main.py inputs/transcript.txt -5         # Creates outputs/transcript_minus_5s.txt
  python main.py inputs/file.txt 10 -o output.txt # Creates output.txt in current directory
        """
    )
    
    parser.add_argument('input_file', help='Input transcript file')
    parser.add_argument('adjustment', type=int, 
                       help='Number of seconds to adjust (positive or negative)')
    parser.add_argument('-o', '--output', dest='output_file',
                       help='Output file (if not specified, auto-generates in outputs/ folder)')
    
    # If no arguments provided, show help and example
    if len(sys.argv) == 1:
        print("Timestamp Adjuster")
        print("==================")
        print("Adjusts timestamps in transcript files with format [HH:MM:SS]\n")
        parser.print_help()
        print("\nExample usage:")
        print("  python main.py inputs/transcript.txt 3     # Creates outputs/transcript_plus_3s.txt")
        print("  python main.py inputs/transcript.txt -5    # Creates outputs/transcript_minus_5s.txt")
        print("  python main.py inputs/transcript.txt 10 -o custom.txt  # Creates custom.txt")
        return
    
    args = parser.parse_args()
    
    # Process the file
    success = process_file(args.input_file, args.output_file, args.adjustment)
    
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
