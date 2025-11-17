# XKB to macOS Layout Converter

This tool converts Linux XKB keyboard layouts to macOS .keylayout files. It parses XKB layout files, maps keysyms to Unicode characters, and generates XML-based .keylayout files that can be installed on macOS systems.

## Features

- Parses XKB layout files with multiple layout blocks
- Resolves layout inheritance through `include` statements
- Maps XKB keysyms to Unicode characters
- Handles special characters and dead keys
- Supports different layout variants
- Generates valid macOS .keylayout XML files
- Visualizes keyboard layouts as interactive SVG diagrams

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

## Quick Start

Convert and install a keyboard layout in one go:

```bash
# 1. Convert XKB layout to .keylayout
python3 convert_layout.py --layout dev --output-dir .

# 2. Install the layout (requires sudo)
python3 install_bundle.py dev.keylayout

# 3. Log out and log back in, then add the layout in System Preferences
```

Or with a custom icon:

```bash
# 1. Create your icon (1024x1024 PNG)
# 2. Convert and install with icon (PNG will be auto-converted)
python3 convert_layout.py --layout dev --output-dir .
python3 install_bundle.py --icon my_icon.png dev.keylayout

# Or manually convert first if you prefer
python3 generate_icons.py my_icon.png
python3 install_bundle.py --icon my_icon.icns dev.keylayout
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

### Quick Installation (Recommended)

Use the included `install_bundle.py` script to create a proper bundle and install it:

```bash
# Basic installation (requires sudo for system-wide installation)
python3 install_bundle.py xkb_to_macos/data/dev.keylayout

# With custom icon (PNG or ICNS - PNG will be auto-converted)
python3 install_bundle.py --icon icons/my_icon.png xkb_to_macos/data/dev.keylayout

# User installation (no sudo, but less reliable)
python3 install_bundle.py --user xkb_to_macos/data/dev.keylayout

# Full customization
python3 install_bundle.py \
  --name "My Dev Layout" \
  --bundle-id com.example.keyboardlayout.dev \
  --icon icons/dev.icns \
  --language en-US \
  xkb_to_macos/data/dev.keylayout
```

The script will:
- Create a properly structured `.bundle` with `Info.plist`
- Include your custom icon (if provided)
- Install to `/Library/Keyboard Layouts/` (system-wide, recommended) or `~/Library/Keyboard Layouts/` (user-specific)
- Handle overwriting existing installations

After installation:
1. Log out and log back in (or restart)
2. Open System Preferences/Settings > Keyboard > Input Sources
3. Click "+" and find your layout under "Others"

### Manual Installation

If you prefer to install manually:

1. Copy the generated `.keylayout` file to:
   - `/Library/Keyboard Layouts/` (system-wide, recommended - requires sudo)
   - `~/Library/Keyboard Layouts/` (user-specific, may have compatibility issues)

```bash
# System-wide (recommended)
sudo cp dev.keylayout /Library/Keyboard\ Layouts/

# User-specific
cp dev.keylayout ~/Library/Keyboard\ Layouts/
```

2. Log out and log back in
3. Open System Preferences > Keyboard > Input Sources
4. Click the "+" button and find your layout under "Others"

**Note**: Manual installation using `.keylayout` files (not bundles) will show a default keyboard icon in the menu bar.

### Creating Custom Icons

To create custom icons for your keyboard layouts:

1. Design a 1024x1024 PNG icon (simple design works best for menu bar display)
2. Use directly with the installation script (auto-converts to ICNS):

```bash
python3 install_bundle.py --icon your_icon.png your_layout.keylayout
```

Or manually convert to ICNS first:

```bash
python3 generate_icons.py your_icon.png
python3 install_bundle.py --icon your_icon.icns your_layout.keylayout
```

See `icons/README.md` for detailed icon creation guidelines and requirements.

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

## Tools

### keylayout_viewer.py

Generates interactive SVG visualizations of macOS keyboard layouts.

**Features**:
- Smart layer optimization (hides predictable A-Z mappings)
- Color-coded modifier states
- Interactive tooltips with Unicode codepoints
- Dead key visualization with special markers
- Dynamic legend showing only used modifiers
- Zero external dependencies (stdlib only)

**Usage**:
```bash
# Basic visualization
python3 keylayout_viewer/keylayout_viewer.py layout.keylayout

# With interactive tooltips
python3 keylayout_viewer/keylayout_viewer.py layout.keylayout --interactive

# Specify output file
python3 keylayout_viewer/keylayout_viewer.py layout.keylayout output.svg
```

**Example**:
```bash
# Visualize the generated dev layout
python3 keylayout_viewer/keylayout_viewer.py data/output/dev.keylayout --interactive
```

See `keylayout_viewer/README.md` for more details.

### install_bundle.py

Creates and installs macOS keyboard layout bundles with proper structure and metadata.

**Features**:
- Generates properly structured `.bundle` with `Info.plist`
- Supports custom icons (`.png` or `.icns` format)
- Automatically converts PNG to ICNS format
- Handles system-wide or user-specific installation
- Overwrites existing installations safely
- Follows macOS best practices for keyboard layout bundles

**Usage**:
```bash
python3 install_bundle.py --help
```

See examples in the "Installing the Generated Layout on macOS" section above.

### generate_icons.py

Converts PNG images to ICNS format for use as keyboard layout icons.

**Features**:
- Converts PNG to ICNS with all required sizes
- Uses macOS native tools (`sips`, `iconutil`)
- Generates proper iconset structure

**Usage**:
```bash
# Convert a PNG to ICNS
python3 generate_icons.py your_icon.png

# View icon creation guidelines
python3 generate_icons.py
```

See `icons/README.md` for detailed icon design guidelines.

## Resources

- [docs/INSTALLATION_GUIDE.md](./docs/INSTALLATION_GUIDE.md) - **Complete step-by-step installation guide**
- [docs/keylayout-spec.md](./docs/keylayout-spec.md) - macOS keyboard layout XML specification
- [docs/bundles-and-install-methods.md](./docs/bundles-and-install-methods.md) - Technical details on how macOS keyboard layouts work
- [icons/README.md](./icons/README.md) - Icon creation guidelines

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