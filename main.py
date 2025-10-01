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
    parser.add_argument('-c', '--config', dest='config_file',
                       help='Configuration file path (default: searches for config.yaml)')
    parser.add_argument('-f', '--format', dest='output_format',
                       help='Override output timestamp format (e.g., "[{hours:02d}:{minutes:02d}:{seconds:02d}]")')
    
    # If no arguments provided, show help and example
    if len(sys.argv) == 1:
        print("Timestamp Adjuster")
        print("==================")
        print("Adjusts timestamps in transcript files with configurable formats\n")
        parser.print_help()
        print("\nExample usage:")
        print("  python main.py inputs/transcript.txt 3     # Creates outputs/transcript_plus_3s.txt")
        print("  python main.py inputs/transcript.txt -5    # Creates outputs/transcript_minus_5s.txt")
        print("  python main.py inputs/transcript.txt 10 -o custom.txt  # Creates custom.txt")
        print("  python main.py -c custom.yaml transcript.txt 5  # Uses custom config")
        return
    
    args = parser.parse_args()
    
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
