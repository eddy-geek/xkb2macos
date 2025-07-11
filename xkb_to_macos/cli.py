"""Command-line interface for XKB to macOS layout conversion.

This module provides the command-line interface for the XKB to macOS layout converter.
"""
import argparse
import os
import sys
from typing import List, Optional

from xkb_to_macos.core.converter import (
    parse_xkb_symbols_file,
    resolve_layout,
    generate_macos_layout,
)


def main(args: Optional[List[str]] = None) -> int:
    """Main entry point for the XKB to macOS layout converter.
    
    Args:
        args: Command-line arguments. If None, sys.argv[1:] will be used.
        
    Returns:
        Exit code (0 for success, non-zero for failure).
    """
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Convert an XKB layout to a macOS .keylayout file.')
    parser.add_argument('-l', '--layout', default='dev', help='The layout variant to convert (default: dev)')
    parser.add_argument('-d', '--debug', action='store_true', help='Enable debug output')
    parser.add_argument('-i', '--input', help='Path to the XKB symbols file (default: data/kt.symbols)')
    parser.add_argument('-o', '--output-dir', help='Directory to save the generated .keylayout file')
    parsed_args = parser.parse_args(args)
    
    # Determine the input file path
    if parsed_args.input:
        layout_file = parsed_args.input
    else:
        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        layout_file = os.path.join(script_dir, 'data', 'kt.symbols')

    print(f'Parsing layout file: {layout_file}')

    # Parse the XKB symbols file
    layouts = parse_xkb_symbols_file(layout_file)
    print(f'Parsed {len(layouts)} layout blocks.')

    # Use the specified layout or default to "dev"
    target_layout_name = parsed_args.layout
    if target_layout_name not in layouts:
        print(f"Error: Layout '{target_layout_name}' not found in {layout_file}.")
        print("Available layouts:")
        for layout in sorted(layouts.keys()):
            print(f"  {layout}")
        return 1
        
    # Resolve the layout
    final_map = resolve_layout(target_layout_name, layouts)
    print(f'\nResolved key map for "{target_layout_name}". It has {len(final_map)} keys.')
    
    if parsed_args.debug:
        print('A few keys from the final resolved map:')
        for i, (key, val) in enumerate(final_map.items()):
            if i >= 5:
                break
            print(f'  {key}: {val}')

    # Change to the output directory if specified
    original_dir = os.getcwd()
    if parsed_args.output_dir:
        os.makedirs(parsed_args.output_dir, exist_ok=True)
        os.chdir(parsed_args.output_dir)

    try:
        # Generate the macOS layout file
        output_file = generate_macos_layout(target_layout_name, final_map, parsed_args.debug)
        
        if parsed_args.output_dir:
            print(f'Output file saved to: {os.path.join(parsed_args.output_dir, output_file)}')
    finally:
        # Change back to the original directory
        if parsed_args.output_dir:
            os.chdir(original_dir)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
