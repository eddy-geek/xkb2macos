# macOS Keylayout Specification

This document provides a comprehensive overview of the macOS keylayout file format, focusing on its XML structure, modifier keys, dead keys, and implementation details.

## Table of Contents

- [Overview](#overview)
- [File Format](#file-format)
- [XML Structure](#xml-structure)
- [Modifier Keys](#modifier-keys)
- [Dead Keys](#dead-keys)
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

Modifiers can be combined with spaces, e.g., `anyShift anyOption`.

### Modifier States

Common modifier states include:

1. No modifiers (index="0")
2. Shift (index="1")
3. Option/Alt (index="2")
4. Shift+Option (index="3")
5. Command (index="4")
6. Shift+Command (index="5")
7. Option+Command (index="6")
8. Shift+Option+Command (index="7")

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

## Installation

To install a custom keylayout file:

1. Copy the `.keylayout` file to one of these locations:
   - `/Library/Keyboard Layouts/` (system-wide)
   - `~/Library/Keyboard Layouts/` (user-specific)
2. Optional: Copy the corresponding `.icns` file to the same location
3. Log out and log back in (or restart)
4. Enable the layout in System Preferences/Settings > Keyboard > Input Sources

## Resources

The following resources were used to compile this specification:

1. [Ukelele - Keyboard Layout Editor for macOS](https://software.sil.org/ukelele/)
2. [Install a Custom Keyboard Layout - macOS](https://weibeld.net/mac/custom-keyboard-layout.html)
3. Source code from the xkb-to-macos project's converter.py
4. macOS keylayout files from Ukelele's standard keyboards collection

## Checking dev.keylayout

The file `/Users/eoubrayrie/code/GEEK/xkb-to-macos/xkb_to_macos/data/dev.keylayout` should conform to the specification outlined above. Key aspects to check include:

1. Proper XML structure with all required elements
2. Correct implementation of modifier keys
3. Proper handling of dead keys if present
4. Valid key codes for all key definitions
5. Correct action references for each key
