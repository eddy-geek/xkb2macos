# XKB to macOS Layout Converter

This tool converts Linux XKB keyboard layouts to macOS .keylayout files. It parses XKB layout files, maps keysyms to Unicode characters, and generates XML-based .keylayout files that can be installed on macOS systems.

## Features

- Parses XKB layout files with multiple layout blocks
- Resolves layout inheritance through `include` statements
- Maps XKB keysyms to Unicode characters
- Handles special characters and dead keys
- Supports different layout variants
- Generates valid macOS .keylayout XML files

## Requirements

- Python 3.12 or higher
- `requests` library (for fetching keysym data)

## Installation

1. Clone this repository or download the source code
2. Install the package and its dependencies:

```bash
pip install -e .
```

For development, install with the development dependencies:

```bash
pip install -e ".[dev]"
```

## Usage

### Basic Usage

To convert the default "dev" layout from the included `kt.symbols.xkb` file:

```bash
python3 convert_layout.py
```

Or if installed as a package:

```bash
xkb-to-macos
```

This will generate a `dev.keylayout` file in the current directory.

### Command-Line Options

- `-l, --layout`: Specify which layout variant to convert (default: "dev")
- `-d, --debug`: Enable debug output to help identify mapping issues
- `-i, --input`: Path to the XKB symbols file (default: data/kt.symbols.xkb)
- `-o, --output-dir`: Directory to save the generated .keylayout file

Example:

```bash
python3 convert_layout.py --layout num102 --debug
```

Or if installed as a package:

```bash
xkb-to-macos --layout num102 --debug
```

### Available Layouts

The included `kt.symbols.xkb` file contains several layout variants:

- `accented_qwerty`: Basic QWERTY layout with accented characters
- `dev`: Development layout for 101-key keyboard (default)
- `num`: Brazil layout with numeric keys
- `num102`: Brazil layout for 102-key keyboard
- And more...

To see all available layouts, run the converter with an invalid layout name:

```bash
python3 convert_layout.py --layout invalid
```

Or if installed as a package:

```bash
xkb-to-macos --layout invalid
```

## Installing the Generated Layout on macOS

1. Copy the generated `.keylayout` file to `/Library/Keyboard Layouts/` (system-wide) or `~/Library/Keyboard Layouts/` (user-specific)
2. Log out and log back in
3. Open System Preferences > Keyboard > Input Sources
4. Click the "+" button and find your layout under "Others"

## How It Works

1. **Parsing**: The tool parses the XKB layout file, identifying layout blocks and their key definitions.
2. **Resolving**: It resolves layout inheritance by following `include` statements to build a complete key map.
3. **Mapping**: XKB keysyms are mapped to Unicode characters using both the generated keysym map and built-in mappings.
4. **Generation**: The tool generates an XML-based .keylayout file with the appropriate structure for macOS.

## Development

### Generating the Keysym Map

The tool uses a comprehensive keysym-to-Unicode mapping generated from an online resource. To update this mapping:

```bash
python -m xkb_to_macos.utils.generate_keysym_map
```

This will create/update the `mapping_generated.py` file in the package.

### Running Tests

To verify that the converter is working correctly:

```bash
pytest
```

Or for more detailed test output:

```bash
pytest -v
```

To run tests with coverage reporting:

```bash
pytest --cov=xkb_to_macos
```

## Troubleshooting

### Missing Keysyms

If some characters aren't displaying correctly in the generated layout, run the converter with the `--debug` flag to identify unmapped keysyms:

```bash
python3 convert.py --debug
```

You can then add the missing mappings to the `special_keysyms` dictionary in `convert.py`.

### Layout Not Found

If you get an error that your layout wasn't found, check the available layouts in the XKB file and make sure you're using the correct name.

## Resources

[My MacOS Keyboard layout spec summary](./docs/keylayout-spec.md)

[Layout installation](./docs/installation.md)

## License

This project is open source and available under the MIT License.



## Notes
- The main goal is to convert an XKB keyboard layout file (`data/kt.symbols`) into a macOS compatible `.keylayout` file.
- The process involves parsing the XKB file, mapping XKB keysyms to Unicode/macOS key codes, and generating the final XML-based `.keylayout` file.
- The `generate_keysym_map.py` script successfully fetched keysym data and created `mapping_generated.py`.
- The parser in `convert.py` can now handle multiple `xkb_symbols` blocks and resolve `include` statements to build a complete layout map.
- We've successfully implemented the XML generation logic to create a valid macOS `.keylayout` file.
- The conversion process is now working end-to-end, generating a usable `dev.keylayout` file.

## Task List
- [x] Finalize the `generate_keysym_map.py` script to create a comprehensive keysym to Unicode mapping.
- [x] Parse the XKB layout file (`data/kt.symbols`), including handling `include` statements.
- [x] Integrate the generated keysym map (`mapping_generated.py`) into the conversion process.
- [x] Implement the mapping logic from XKB key definitions to macOS key map entries.
- [x] Generate the final macOS `.keylayout` file from the resolved layout.
- [ ] Write small tests to verify the parsing and mapping logic.
- [ ] Add support for additional layout variants beyond the default "dev" layout.
- [ ] Improve error handling for missing keysyms and invalid mappings.

## Current Goal
Write tests and improve error handling.