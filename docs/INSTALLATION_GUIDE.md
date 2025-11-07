# Complete Installation Guide

This guide walks you through the complete process of converting an XKB layout and installing it on macOS.

## Prerequisites

- Python 3.12 or higher
- macOS (tested on Big Sur and later)
- Administrator access (for system-wide installation)

## Step-by-Step Process

### 1. Convert XKB Layout to .keylayout

First, convert your XKB layout to macOS format:

```bash
cd xkb_to_macos

# Convert the default "dev" layout
python3 convert_layout.py

# Or specify a different layout
python3 convert_layout.py --layout num102

# Save to a specific directory
python3 convert_layout.py --layout dev --output-dir ./layouts
```

This creates a `.keylayout` file (e.g., `dev.keylayout`).

### 2. (Optional) Create a Custom Icon

If you want a custom icon in the menu bar:

#### Option A: Create from scratch

1. Design a 1024x1024 PNG image:
   - Keep it simple (will be displayed at ~16-22px)
   - Use 1-3 characters or a simple symbol
   - Ensure good contrast for light/dark modes

2. Convert to ICNS:
   ```bash
   python3 generate_icons.py your_icon.png
   ```

#### Option B: Use online tools

Upload your PNG to:
- https://anyconv.com/png-to-icns-converter/
- https://cloudconvert.com/png-to-icns

### 3. Install the Layout

#### Recommended: System-wide installation

```bash
cd xkb_to_macos

# Basic installation (requires sudo)
python3 tools/install_bundle.py data/dev.keylayout

# With custom icon
python3 tools/install_bundle.py --icon icons/dev.png data/dev.keylayout

# With custom name and settings
python3 tools/install_bundle.py \
  --name "My Dev Layout" \
  --bundle-id com.mycompany.keyboardlayout.dev \
  --icon icons/dev.icns \
  --language en-US \
  data/dev.keylayout
```

You'll be prompted for your password (sudo) to install to `/Library/Keyboard Layouts/`.

#### Alternative: User-specific installation

```bash
python3 install_bundle.py --user dev.keylayout
```

**Note**: User installations (`~/Library/Keyboard Layouts/`) may not work reliably in all applications. System-wide installation is recommended.

### 4. Activate the Layout

1. **Log out and log back in** (or restart your Mac)
   - This is required for macOS to detect the new layout

2. **Open System Preferences/Settings**:
   - Go to `Keyboard` > `Input Sources`
   - Click the `+` button
   - Look under "Others" or search for your layout name
   - Select it and click "Add"

3. **Test the layout**:
   - Switch to your new layout using the menu bar icon
   - Open a text editor and test the keys
   - Verify special characters and modifiers work correctly

## Troubleshooting

### Layout doesn't appear in System Preferences

**Solutions**:
1. Restart your Mac (logout may not be sufficient)
2. Check the installation location:
   ```bash
   ls -la /Library/Keyboard\ Layouts/
   # or for user install:
   ls -la ~/Library/Keyboard\ Layouts/
   ```
3. Verify the bundle structure:
   ```bash
   find /Library/Keyboard\ Layouts/dev.bundle
   ```
4. Check Console.app for errors related to keyboard layouts

### Layout appears but won't activate

**Solutions**:
1. Remove the layout from Input Sources and re-add it
2. If installed to `~/Library`, try system installation instead:
   ```bash
   python3 install_bundle.py dev.keylayout
   ```
3. Verify the `Info.plist` is correct:
   ```bash
   cat /Library/Keyboard\ Layouts/dev.bundle/Contents/Info.plist
   ```

### System Preferences crashes when adding layout

**Solutions**:
1. The bundle may be corrupted. Reinstall:
   ```bash
   python3 install_bundle.py dev.keylayout
   ```
2. Check if the icon file is valid (if using custom icon)
3. Try without an icon first:
   ```bash
   python3 install_bundle.py dev.keylayout
   ```

### Keys don't produce expected characters

**Solutions**:
1. Check the original `.keylayout` file for errors
2. Re-convert with debug output:
   ```bash
   python3 convert_layout.py --layout dev --debug
   ```
3. Test in multiple applications (some apps may override layouts)

### Duplicate layouts appearing

**Solutions**:
1. Remove old installations:
   ```bash
   sudo rm -rf /Library/Keyboard\ Layouts/dev.bundle
   rm -rf ~/Library/Keyboard\ Layouts/dev.bundle
   ```
2. Remove from Input Sources in System Preferences
3. Restart and reinstall

## Updating an Existing Layout

To update a layout you've already installed:

```bash
cd xkb_to_macos
# Simply reinstall - the script will overwrite the existing bundle
python3 tools/install_bundle.py data/dev.keylayout
python3 tools/install_bundle.py --icon ./icons/dev-light.png data/dev.keylayout
# Then remove and re-add in System Preferences
# (or just restart your Mac)
```

## Uninstalling a Layout

1. Remove from System Preferences Input Sources

2. Delete the bundle:
   ```bash
   # System installation
   sudo rm -rf /Library/Keyboard\ Layouts/dev.bundle
   
   # User installation
   rm -rf ~/Library/Keyboard\ Layouts/dev.bundle
   ```

3. Log out and log back in

## Advanced Usage

### Creating bundles without installing

Useful for testing or distribution:

```bash
python3 tools/install_bundle.py --no-install --output ./dist data/dev.keylayout
```

This creates the bundle in `./dist/` without installing it.

### Multiple layouts in one bundle

Currently not directly supported by the script, but you can manually:

1. Create separate `.keylayout` files
2. Place them all in the same `.lproj` directory
3. Update `Info.plist` with multiple `KLInfo_*` entries

See [docs/installation.md](docs/installation.md) for details on bundle structure.

### Custom language/region settings

```bash
python3 tools/install_bundle.py --language fr-FR data/dev.keylayout
```

This affects:
- The `.lproj` directory name (`fr_FR.lproj`)
- The `TISIntendedLanguage` in `Info.plist`
- How macOS categorizes the layout

## Best Practices

1. **Always use system installation** (`/Library/Keyboard Layouts/`) unless you have a specific reason not to

2. **Test thoroughly** before distributing:
   - Test in multiple applications
   - Test all modifier combinations
   - Test in both light and dark modes (for icon visibility)

3. **Use descriptive names**:
   - Bundle name: "Dev Layout" (user-friendly)
   - Bundle ID: "com.yourcompany.keyboardlayout.dev" (unique)

4. **Version your layouts**:
   ```bash
   python3 tools/install_bundle.py --version 1.1 data/dev.keylayout
   ```

5. **Keep icons simple**:
   - 1-3 characters work best
   - High contrast
   - Test at small sizes

## Distribution

To distribute your layout to others:

1. Create the bundle without installing:
   ```bash
   python3 tools/install_bundle.py --no-install --output ./dist data/dev.keylayout
   ```

2. Compress the bundle:
   ```bash
   cd dist
   zip -r dev-layout.zip dev.bundle
   ```

3. Provide installation instructions:
   ```
   1. Unzip dev-layout.zip
   2. Copy dev.bundle to /Library/Keyboard Layouts/
      (requires sudo: sudo cp -R dev.bundle /Library/Keyboard\ Layouts/)
   3. Log out and log back in
   4. Add layout in System Preferences > Keyboard > Input Sources
   ```

## Further Reading

- [docs/installation.md](docs/installation.md) - Detailed technical information about macOS keyboard layouts
- [docs/keylayout-spec.md](docs/keylayout-spec.md) - macOS keyboard layout XML specification
- [icons/README.md](icons/README.md) - Icon creation guidelines

## Getting Help

If you encounter issues:

1. Check this guide's troubleshooting section
2. Review the Console.app for error messages
3. Verify your bundle structure matches the examples
4. Check that your `.keylayout` file is valid XML

For XKB conversion issues, use the `--debug` flag:
```bash
python3 convert_layout.py --layout dev --debug
```
