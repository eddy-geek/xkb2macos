# macOS Keyboard Layout Installation Guide

How keyboard layouts are installed, managed, and detected on macOS.

## Installation Paths

### System Layouts (Read-Only)
- **Path**: `/System/Library/Keyboard Layouts/AppleKeyboardLayouts.bundle`
- **Access**: Protected by System Integrity Protection (SIP) since macOS Big Sur (v11)
- **Format**: Optimized binary bundle containing all default Apple keyboard layouts
- **Editability**: Cannot be modified without disabling SIP (not recommended)

### User-Installed Layouts (Editable)

macOS supports two locations for custom keyboard layouts:

1. **System-wide installation** (Recommended)
   - **Path**: `/Library/Keyboard Layouts/`
   - **Access**: Requires administrator privileges
   - **Scope**: Available to all users on the system
   - **Reliability**: Most stable; layouts work consistently across all applications

2. **User-specific installation**
   - **Path**: `~/Library/Keyboard Layouts/`
   - **Access**: User-level permissions only
   - **Scope**: Available only to the current user
   - **Known Issues**: 
     - Layouts may appear in the input source list but fail to activate in some applications
     - Reported bugs on various macOS versions (High Sierra, Mojave, etc.)
     - May work in some apps (e.g., VS Code) but not others (e.g., Mail, Reminders)

**Best Practice**: Install custom layouts to `/Library/Keyboard Layouts/` for maximum compatibility.

## File Formats

### .keylayout Files
- **Format**: XML-based text files
- **Structure**: Defines key mappings for each key on the keyboard
- **Usage**: Can be installed directly or bundled
- **Limitations**: 
  - Cannot customize the menu bar icon (shows default keyboard icon)
  - Simpler structure, easier to create and edit

### .bundle Format
- **Format**: macOS bundle (directory structure)
- **Structure**:
  ```
  YourLayout.bundle/
  ├── Contents/
  │   ├── Info.plist
  │   └── Resources/
  │       ├── <language>_<REGION>.lproj/
  │       │   └── YourLayout.keylayout
  │       └── YourLayout.icns (optional icon)
  ```
- **Advantages**:
  - Supports custom menu bar icons
  - Allows localization
  - Can bundle multiple layouts together
  - More professional distribution format
- **Known Issues**:
  - Some macOS versions (e.g., High Sierra) crash System Preferences when bundles are installed
  - More complex structure

### Bundle Configuration (Info.plist)

Required keys for proper layout detection:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleIdentifier</key>
    <string>com.yourcompany.keyboardlayout.layoutname</string>
    
    <key>CFBundleName</key>
    <string>Your Layout Name</string>
    
    <key>CFBundleVersion</key>
    <string>1.0</string>
    
    <key>KLInfo_YourLayoutName</key>
    <dict>
        <key>TISInputSourceID</key>
        <string>com.yourcompany.keyboardlayout.layoutname.yourlayoutname</string>
        
        <key>TISIntendedLanguage</key>
        <string>en-US</string>
    </dict>
</dict>
</plist>
```

**Key Requirements**:
- `CFBundleIdentifier`: Must contain `.keyboardlayout.` (before macOS Leopard, had to start with `com.apple.keyboardlayout`)
- `TISInputSourceID`: Unique identifier in reverse-DNS format; typically `bundleID + ".keylayout." + layoutname`
- `TISIntendedLanguage`: Language code in BCP 47 format (e.g., `en-US`, `fr-FR`, `de-DE`)
- `KLInfo_<layoutname>`: Dictionary key must match the layout name exactly, including spaces and punctuation

**Localization Directory**: The `.lproj` directory name must match the language/region format: `<language>_<REGION>.lproj` (e.g., `en_US.lproj`, `fr_FR.lproj`)

## Default Layouts

### Storage Format
- Default Apple layouts are stored in a compressed, optimized binary format within `AppleKeyboardLayouts.bundle`
- The bundle contains `.dat` files (e.g., `AppleKeyboardLayouts-L.dat`) that store:
  - Keyboard layout definitions
  - Icon resources (`.icns` files) in binary format
  - Localization data

### Compression and Optimization
- Layouts are "optimized for deployment" and not directly readable as XML
- Icons are embedded in the `.dat` files as hex-encoded binary data
- This optimization reduces file size and improves loading performance

### Modification Restrictions
- Cannot be modified on macOS Big Sur (v11) and later due to SIP
- Attempting to edit requires:
  1. Booting into Recovery Mode (Command+R)
  2. Disabling SIP with `csrutil disable`
  3. Making changes
  4. Re-enabling SIP (strongly recommended for security)
- **Not recommended**: Modifying system layouts can break system stability

### Extracting Default Layouts
To use a default layout as a template:
- Use **Ukelele**: `File > New From Current Input Source`
- This creates a new layout based on the currently active keyboard without needing to find the original `.keylayout` file

## Detection and System Integration

### How Layouts Are Detected

1. **File System Scanning**
   - macOS scans `/Library/Keyboard Layouts/` and `~/Library/Keyboard Layouts/` at login
   - Layouts are registered with the Text Input Source Services API
   - Changes require logout/login or manual refresh

2. **Preference Storage**
   - Active keyboard layouts are stored in: `~/Library/Preferences/com.apple.HIToolbox.plist`
   - Key: `AppleSelectedInputSources`
   - Subkey: `KeyboardLayout Name`
   - This file is cached; changes may not appear immediately

3. **System Preferences Display**
   - Layouts appear in: `System Preferences > Keyboard > Input Sources > + > Others`
   - Filtered by language/region settings
   - Custom layouts typically appear under "Others" category

### Cache and Refresh Issues

Common problems:
- **Stale cache**: System Preferences may show outdated layout list
- **Duplicate entries**: Installing/reinstalling layouts can create duplicates
- **Layouts not appearing**: May require:
  - Logout/login
  - System restart
  - Manually removing and re-adding in System Preferences

**Workaround**: Run `defaults read ~/Library/Preferences/com.apple.HIToolbox.plist dummy` to flush the plist cache.

## Software Management Approaches

### Ukelele (Standard Approach)

**Installation Method**:
- Provides GUI for creating and editing layouts
- Saves directly to `/Library/Keyboard Layouts/` or `~/Library/Keyboard Layouts/`
- Automatically generates proper bundle structure with `Info.plist`
- Handles localization and icon integration

**Update Workflow**:
1. Edit layout in Ukelele
2. Save to installation directory (overwrites existing file)
3. Remove layout from System Preferences input sources
4. Re-add layout from input sources list
5. No restart required (in most cases)

**Best Practices**:
- Always set language/region in `Keyboard Layouts` tab
- Configure localization in `Localisations` tab
- Use `File > New From Current Input Source` to base layouts on existing ones
- Test in multiple applications before distribution

### Keyman (Application-Based Approach)

**Installation Method**:
- Installs as a standalone input method application
- Keyboards stored in: `~/Documents/Keyman-Keyboards/` (older versions) or `/Library/Application Support/` (v18+)
- Uses `.kmp` (Keyman Package) format, not standard `.keylayout`
- Appears as a separate input source, not a keyboard layout

**Update Workflow**:
1. Download/install `.kmp` package via Keyman Configuration
2. Keyman manages installation automatically
3. Keyboards can be enabled/disabled without uninstalling
4. Updates handled through Keyman's update mechanism

**Architecture**:
- Keyman is an **input method**, not a keyboard layout
- Runs as a background process
- Intercepts keyboard input and translates it
- More powerful than layouts (supports complex scripts, context-sensitive rules)
- Requires Keyman application to be running

**Advantages**:
- Cross-platform consistency (Windows, macOS, Linux, mobile)
- Supports complex input methods (e.g., phonetic input, dead keys, multi-stage composition)
- Built-in keyboard repository and update system
- User-friendly installation (drag-and-drop `.kmp` files)

**Disadvantages**:
- Requires additional software installation
- Not native macOS keyboard layouts
- May have compatibility issues with some applications
- Additional system permissions required

### Comparison: Ukelele vs. Keyman

| Aspect | Ukelele Layouts | Keyman |
|--------|----------------|---------|
| **Format** | Native `.keylayout`/`.bundle` | `.kmp` packages (input method) |
| **Installation** | System/user keyboard layout directories | Application-managed storage |
| **Integration** | Native macOS input source | Separate input method application |
| **Complexity** | Simple key remapping | Complex input rules, context-sensitive |
| **Dependencies** | None (native) | Requires Keyman app running |
| **Updates** | Manual file replacement | Managed by Keyman |
| **Distribution** | Files or bundles | Packages with metadata |
| **Portability** | macOS only | Cross-platform |

## Installation Best Practices

### For Developers

1. **Use bundle format** for professional distribution
2. **Include proper `Info.plist`** with all required keys
3. **Set `TISIntendedLanguage`** to ensure proper detection
4. **Test on multiple macOS versions** (behavior varies)
5. **Provide installation instructions** for both paths
6. **Include an `.icns` icon** for better user experience
7. **Use unique `CFBundleIdentifier`** to avoid conflicts

### For Users

1. **Prefer `/Library/Keyboard Layouts/`** over `~/Library/Keyboard Layouts/`
2. **Use `sudo` or administrator access** to copy to system directory:
   ```bash
   sudo cp -R YourLayout.bundle /Library/Keyboard\ Layouts/
   ```
3. **Log out and log back in** after installation
4. **Add layout via System Preferences**:
   - `System Preferences > Keyboard > Input Sources > + > Others`
5. **If layout doesn't work**, try:
   - Restarting the system
   - Removing and re-adding the layout
   - Checking Console.app for errors
   - Verifying `Info.plist` syntax

### Troubleshooting

**Layout appears but won't activate**:
- Check if installed in `~/Library/Keyboard Layouts/` → move to `/Library/Keyboard Layouts/`
- Verify `TISIntendedLanguage` is set correctly
- Check `.lproj` directory naming matches language code

**System Preferences crashes**:
- Try installing `.keylayout` file instead of `.bundle`
- Check `.icns` file isn't corrupted
- Verify `Info.plist` XML syntax

**Layout not appearing in list**:
- Flush plist cache: `defaults read ~/Library/Preferences/com.apple.HIToolbox.plist dummy`
- Log out and log back in
- Check file permissions (should be readable by all users)

**Duplicate layouts appearing**:
- Remove old versions from both `/Library/Keyboard Layouts/` and `~/Library/Keyboard Layouts/`
- Clear input sources in System Preferences
- Restart system

## References

- [Apple Technical Note TN2056: Installable Keyboard Layouts](https://developer.apple.com/library/archive/technotes/tn2056/)
- [Text Input Source Services API](https://developer.apple.com/documentation/carbon/text_input_source_services)
- [Ukelele Keyboard Layout Editor](https://software.sil.org/ukelele/)
- [Keyman for macOS](https://keyman.com/mac/)
- [BCP 47 Language Tags](https://www.rfc-editor.org/info/bcp47)
