# macOS Keylayout Specification

This document provides a comprehensive overview of the macOS keylayout file format, focusing on its XML structure, modifier keys, dead keys, and implementation details.

## Table of Contents

- [Overview](#overview)
- [File Format](#file-format)
- [XML Structure](#xml-structure)
- [Modifier Keys](#modifier-keys)
- [Dead Keys](#dead-keys)
- [Apple Silicon Function Keys](#apple-silicon-function-keys)
- [System Bundle Files](#system-bundle-files)
- [Installation](#installation)
- [Resources](#resources)

## Overview

macOS keylayout files (.keylayout) are XML-based files that define keyboard layouts for macOS. They map physical keys to character outputs and handle various modifier states and special keys like dead keys. These files can be created manually or with tools like Ukelele.

## File Format

- File extension: `.keylayout`
- Format: XML
- Encoding: UTF-8
- Optional companion file: `.icns` (icon file for the input menu)

## XML Structure

> **XKB Compatibility Note:** Unlike XKB layouts which use a text-based format with sections like `xkb_symbols`, macOS uses an XML-based format. The conversion process involves mapping XKB key codes (like `AD01`, `AC02`) to macOS virtual key codes, and mapping XKB levels to macOS modifier states.

A keylayout file consists of the following main elements:

### Root Element

```xml
<keyboard group="126" id="" name="LayoutName">
    <!-- Child elements go here -->
</keyboard>
```

Attributes:
- `group`: Typically "126" for standard keyboard layouts
- `id`: Optional identifier
- `name`: The name of the keyboard layout

### Layouts Element

```xml
<layouts>
    <layout first="0" last="0" mapSet="ANSI" modifiers="modifiers"/>
</layouts>
```

Defines the range of layouts included in the file.

### Modifier Map

```xml
<modifierMap id="modifiers" defaultIndex="0">
    <keyMapSelect mapIndex="0">
        <modifier keys=""/>
    </keyMapSelect>
    <keyMapSelect mapIndex="1">
        <modifier keys="anyShift"/>
    </keyMapSelect>
    <keyMapSelect mapIndex="2">
        <modifier keys="anyOption"/>
    </keyMapSelect>
    <keyMapSelect mapIndex="3">
        <modifier keys="anyShift anyOption"/>
    </keyMapSelect>
    <!-- Additional modifier combinations -->
</modifierMap>
```

The modifier map defines how different modifier keys affect the keyboard layout.

### Key Map Set

```xml
<keyMapSet id="ANSI">
    <keyMap index="0">
        <!-- Keys with no modifiers -->
    </keyMap>
    <keyMap index="1">
        <!-- Keys with Shift modifier -->
    </keyMap>
    <keyMap index="2">
        <!-- Keys with Option modifier -->
    </keyMap>
    <keyMap index="3">
        <!-- Keys with Shift+Option modifiers -->
    </keyMap>
    <!-- Additional key maps -->
</keyMapSet>
```

Contains the actual key mappings for different modifier states.

### Key Definitions

```xml
<key code="0">
    <action id="a">
        <when state="none" output="a"/>
        <when state="shift" output="A"/>
        <!-- Additional states -->
    </action>
</key>
```

Each key is defined with a code attribute corresponding to the macOS virtual key code.

> **XKB Compatibility Note:** When converting from XKB layouts, a mapping table is used to convert XKB key names (like `AC01` for the 'A' key) to macOS virtual key codes (like `0`). The XKB key symbols for each level are then mapped to the corresponding macOS modifier states.

### Actions

```xml
<actions>
    <action id="action_id">
        <when state="none" output="a"/>
        <!-- Additional states -->
    </action>
    <!-- Additional actions -->
</actions>
```

The actions section defines character outputs for different states.

## Modifier Keys

macOS keylayout files support the following modifier keys:

- `command` (⌘)
- `control` (⌃)
- `option` (⌥)
- `shift` (⇧)
- `caps` (⇪)
- `anyShift` (either shift key)
- `anyOption` (either option key)
- `anyControl` (either control key)
- `command?` (optional command)
- `shift?` (optional shift)
- `option?` (optional option)
- `control?` (optional control)

> **XKB Compatibility Note:** When mapping from XKB layouts to macOS, the `Option` key (⌥) typically corresponds to XKB's `AltGr` or `ISO_Level3_Shift`. In XKB layouts, the third level (accessed with AltGr) maps to the Option modifier in macOS, and the fourth level (Shift+AltGr) maps to Shift+Option.

Modifiers can be combined with spaces, e.g., `anyShift anyOption`.

### Modifier States

Common modifier states include:

1. No modifiers (index="0") → XKB Level 1
2. Shift (index="1") → XKB Level 2
3. Option/Alt (index="2") → XKB Level 3 (AltGr)
4. Shift+Option (index="3") → XKB Level 4 (Shift+AltGr)
5. Command (index="4")
6. Shift+Command (index="5")
7. Option+Command (index="6")
8. Shift+Option+Command (index="7")

> **XKB Compatibility Note:** The first four modifier states directly correspond to XKB's four levels. When converting from XKB to macOS layouts, the mapping is straightforward for these levels. XKB doesn't have direct equivalents for Command-based modifiers, as these are macOS-specific.

## Dead Keys

Dead keys are special keys that don't produce output immediately but modify the next key pressed. They're commonly used for diacritical marks in various languages.

### Implementation

Dead keys are implemented using the following structure:

```xml
<action id="dead_key_id">
    <when state="none" next="dead_key_state"/>
</action>

<!-- In the actions section -->
<action id="dead_key_state">
    <when state="none" output=""/>
    <when state="a" output="á"/>
    <when state="e" output="é"/>
    <!-- Additional character combinations -->
    <!-- Terminator when no valid combination exists -->
    <when state="dead_key_state" output="`"/>
</action>
```

### Common Dead Keys

- Acute accent (´)
- Grave accent (`)
- Circumflex (^)
- Tilde (~)
- Diaeresis/Umlaut (¨)
- Cedilla (¸)
- Ring (˚)
- Caron (ˇ)
- Macron (¯)
- Breve (˘)
- Dot above (˙)
- Double acute (˝)
- Ogonek (˛)

### Terminators

A terminator is the character output when a dead key is pressed followed by a key that doesn't form a valid combination. It's typically the dead key's own symbol.

## Apple Silicon Function Keys

Apple Silicon Macs have specific considerations for function keys in keyboard layouts:

### Function Key Behavior

- Function keys (F1-F12) on Apple Silicon Macs can have dual functionality:
  - Default behavior: Media controls, brightness, volume, etc.
  - Function key behavior: Standard F1-F12 functionality when pressed with the `fn` key

### Special Function Keys

- **Touch ID**: Integrated with the function key row on some models (not directly mappable in keylayout files)
- **Globe Key**: Present on newer Apple keyboards, can be used to switch between keyboard layouts
- **Media Control Keys**: Brightness, volume, media playback controls

### Function Key Codes

Function keys use the following key codes in keylayout files:

| Key | Code | Default Function |
|-----|------|------------------|
| F1  | 122  | Display brightness down |
| F2  | 120  | Display brightness up |
| F3  | 99   | Mission Control |
| F4  | 118  | Spotlight |
| F5  | 96   | Dictation |
| F6  | 97   | Do Not Disturb |
| F7  | 98   | Media previous |
| F8  | 100  | Media play/pause |
| F9  | 101  | Media next |
| F10 | 109  | Mute |
| F11 | 103  | Volume down |
| F12 | 111  | Volume up |

## System Bundle Files

In addition to standalone `.keylayout` files, macOS supports keyboard layout bundles for more advanced functionality, with this structure:


```
MyLayout.bundle/
├── Contents/
│   ├── Info.plist
│   └── Resources/
│       ├── MyLayout.keylayout
│       └── MyLayout.icns
```

### Bundle Advantages

1. **Language Categorization**: Bundles can specify the language category, preventing layouts from being placed in the "Others" group
2. **Multiple Layouts**: A single bundle can contain multiple related layouts
3. **Additional Resources**: Can include documentation, scripts, and other supporting files
4. **Metadata**: Info.plist can contain detailed metadata about the layout

### System Bundle Location

Apple's built-in keyboard layouts are stored in:
```
/System/Library/Keyboard Layouts/AppleKeyboardLayouts.bundle
```

This bundle contains all the system keyboard layouts and is optimized for deployment, making it difficult to use as a reference.

## Installation

### Standalone .keylayout Files

To install a custom keylayout file:

1. Copy the `.keylayout` file to one of these locations:
   - `/Library/Keyboard Layouts/` (system-wide)
   - `~/Library/Keyboard Layouts/` (user-specific)
2. Optional: Copy the corresponding `.icns` file to the same location
3. Log out and log back in (or restart)
4. Enable the layout in System Preferences/Settings > Keyboard > Input Sources

### Bundle Files

To install a keyboard layout bundle:

1. Copy the `.bundle` directory to one of these locations:
   - `/Library/Keyboard Layouts/` (system-wide)
   - `~/Library/Keyboard Layouts/` (user-specific)
2. Log out and log back in (or restart)
3. Enable the layout in System Preferences/Settings > Keyboard > Input Sources

### Permissions and SIP

- System Integrity Protection (SIP) prevents modifications to system keyboard layouts
- User-installed layouts should always go in one of the Library locations mentioned above
- On newer macOS versions, you may need to grant permissions for third-party keyboard layouts

## Resources

The following resources were used to compile this specification:

1. [Ukelele - Keyboard Layout Editor for macOS](https://software.sil.org/ukelele/)
2. [Install a Custom Keyboard Layout - macOS](https://weibeld.net/mac/custom-keyboard-layout.html)
3. [Apple Developer Forums - macOS keyboard definition location](https://developer.apple.com/forums/thread/123251)
4. [GitHub - macOS keyboard layout generator](https://github.com/kirelagin/macos-keyboard-layout)
5. [How to use the function keys on your Mac - Apple Support](https://support.apple.com/en-us/102439)



## Analysis of dev.keylayout

The file `/Users/eoubrayrie/code/GEEK/xkb-to-macos/xkb_to_macos/data/dev.keylayout` has been analyzed for compliance with the macOS keylayout specification. Here are the findings:

### Structure Analysis

```xml
<?xml version="1.0" ?>
<keyboard group="0" id="-1" name="Custom - dev" maxout="1">
    <layouts>
        <layout first="0" last="0" mapSet="-1" modifiers="-1">
            <keyMapSet id="-1">
                <!-- Key definitions -->
            </keyMapSet>
        </layout>
    </layouts>
</keyboard>
```

### Compliance Assessment

1. **XML Structure**:
   - The file follows the basic XML structure required for keylayout files
   - Contains the root `keyboard` element with appropriate attributes
   - Includes `layouts`, `layout`, and `keyMapSet` elements
   - Uses direct key-to-action mapping

2. **Non-standard Values**:
   - Uses non-standard values for several attributes:
     - `group="0"` (standard is typically "126")
     - `id="-1"` (should be a meaningful identifier)
     - `mapSet="-1"` (should reference a valid mapSet)
     - `modifiers="-1"` (should reference a valid modifier map)
   - Includes a non-standard `maxout="1"` attribute

3. **Modifier Implementation**:
   - Does not include a separate `modifierMap` section
   - Instead uses numbered action IDs (e.g., `k12_0`, `k12_1`, etc.) to represent different modifier states:
     - `_0`: No modifier
     - `_1`: Shift
     - `_2`: Option/Alt
     - `_3`: Shift+Option

4. **Key Definitions**:
   - Each key has a proper `code` attribute with a numeric value
   - Contains multiple `action` elements per key for different modifier states
   - Each action has an `output` attribute with the character to be produced

5. **Character Coverage**:
   - Includes a comprehensive set of characters:
     - Basic Latin letters and numbers
     - Accented characters (á, é, è, etc.)
     - Special symbols (•, ¶, ®, ™, etc.)
     - Diacritical marks (̀, ́, ̂, ̈, etc.)
     - Mathematical and technical symbols (×, ✕, etc.)

6. **Dead Keys**:
   - No explicit dead key implementation using the `next` attribute
   - Some diacritical marks are directly mapped to keys with modifiers
   - This approach doesn't allow for true dead key functionality (combining with subsequent keystrokes)

### Conclusion

The dev.keylayout file uses a simplified, non-standard approach to keyboard layout definition. While it will likely work for basic character mapping, it deviates from the standard macOS keylayout specification in several ways:

1. Missing proper modifier map structure
2. Non-standard attribute values
3. No true dead key implementation
4. Simplified structure without separate actions section

These deviations may limit functionality, particularly for complex layouts requiring dead keys or advanced modifier combinations. For production use, it would be advisable to restructure the file to follow the standard specification more closely, especially if compatibility with future macOS versions is a concern.
