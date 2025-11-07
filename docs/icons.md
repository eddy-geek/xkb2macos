# Keyboard Layout Icons

## Creating Custom Icons

To create custom icons for your keyboard layouts:

1. **Design your icon** (1024x1024 PNG recommended):
   - Keep it simple - it will be displayed small in the menu bar
   - Use 1-3 characters or a simple symbol
   - Include transparency if desired
   - Save as PNG format

2. **Convert to ICNS**:
   ```bash
   python3 generate_icons.py your_icon.png
   ```
   
   Or manually:
   ```bash
   # Create iconset directory
   mkdir MyIcon.iconset
   
   # Generate all sizes
   sips -z 16 16     your_icon.png --out MyIcon.iconset/icon_16x16.png
   sips -z 32 32     your_icon.png --out MyIcon.iconset/icon_16x16@2x.png
   sips -z 32 32     your_icon.png --out MyIcon.iconset/icon_32x32.png
   sips -z 64 64     your_icon.png --out MyIcon.iconset/icon_32x32@2x.png
   sips -z 128 128   your_icon.png --out MyIcon.iconset/icon_128x128.png
   sips -z 256 256   your_icon.png --out MyIcon.iconset/icon_128x128@2x.png
   sips -z 256 256   your_icon.png --out MyIcon.iconset/icon_256x256.png
   sips -z 512 512   your_icon.png --out MyIcon.iconset/icon_256x256@2x.png
   sips -z 512 512   your_icon.png --out MyIcon.iconset/icon_512x512.png
   sips -z 1024 1024 your_icon.png --out MyIcon.iconset/icon_512x512@2x.png
   
   # Convert to ICNS
   iconutil -c icns MyIcon.iconset
   
   # Clean up
   rm -rf MyIcon.iconset
   ```

3. **Use with install_bundle.py**:
   ```bash
   python3 install_bundle.py --icon icons/MyIcon.icns your_layout.keylayout
   ```

## Online Tools

If you prefer not to use command-line tools:
- https://anyconv.com/png-to-icns-converter/
- https://cloudconvert.com/png-to-icns

## Icon Design Tips

- **Menu bar display**: Icons appear at ~16-22px in the menu bar
- **Contrast**: Ensure good contrast for both light and dark modes
- **Simplicity**: Avoid complex details that won't be visible when small
- **Text**: If using text, use bold, sans-serif fonts
- **Testing**: Test your icon in both light and dark macOS themes

See also [Designing Menu Bar Extras](https://bjango.com/articles/designingmenubarextras/) to make 'template' (monochrome) icons.