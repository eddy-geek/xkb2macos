"""Core functionality for XKB to macOS layout conversion.

This module contains the main functionality for parsing XKB layout files,
resolving layout inheritance, and generating macOS .keylayout files.
"""
import os
import re
import sys
from typing import Dict, List, Optional, Set, Tuple, Any
import xml.etree.ElementTree as ET
from xml.dom import minidom

from xkb_to_macos.utils.mapping import XKB_TO_MACOS_KEYCODE
from xkb_to_macos.utils.mapping_generated import KEYSYM_MAP


def parse_xkb_symbols_file(file_path: str) -> Dict[str, Dict[str, Any]]:
    """Parse the XKB symbols file to extract layout blocks and key definitions.
    
    Args:
        file_path: Path to the XKB symbols file.
        
    Returns:
        A dictionary mapping layout names to their key definitions and includes.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Remove comments to simplify parsing
    content = re.sub(r'//.*', '', content)

    layouts = {}
    # Regex to find the start of an xkb_symbols block
    layout_start_pattern = re.compile(r'(?:default\s+)?xkb_symbols\s+"([^"]+)"\s*\{')
    # Regex to find key definitions within a block
    key_pattern = re.compile(r'key\s+<([A-Z0-9_]+)>\s*\{\s*(.*?)\s*\};', re.DOTALL)
    # Regex to find symbol groups like '[ a, A ]'
    group_pattern = re.compile(r'\[(.*?)\]')
    # Regex to find include statements
    include_pattern = re.compile(r'include\s+"([^"]+)"')

    for start_match in layout_start_pattern.finditer(content):
        layout_name = start_match.group(1)
        block_start_pos = start_match.end()
        
        # Find the matching closing brace for the block
        brace_level = 1
        block_end_pos = -1
        for i in range(block_start_pos, len(content)):
            if content[i] == '{':
                brace_level += 1
            elif content[i] == '}':
                brace_level -= 1
                if brace_level == 0:
                    block_end_pos = i
                    break
        
        if block_end_pos == -1:
            continue # Malformed block

        layout_content = content[block_start_pos:block_end_pos]

        # Parse includes
        includes = [m.group(1) for m in include_pattern.finditer(layout_content)]

        # Parse key definitions
        key_definitions = {}
        for match in key_pattern.finditer(layout_content):
            key_name = match.group(1)
            key_content_inner = match.group(2)

            groups = []
            for group_match in group_pattern.finditer(key_content_inner):
                keysyms_str = group_match.group(1)
                keysyms = [s.strip() for s in keysyms_str.split(',')]
                groups.append(keysyms)

            if groups:
                key_definitions[key_name] = groups
        
        layouts[layout_name] = {'keys': key_definitions, 'includes': includes}

    return layouts


def resolve_layout(layout_name: str, all_layouts: Dict[str, Dict[str, Any]], 
                  seen: Optional[Set[str]] = None) -> Dict[str, List[List[str]]]:
    """Recursively resolve includes to build a complete key map for a layout.
    
    Args:
        layout_name: The name of the layout to resolve.
        all_layouts: Dictionary of all available layouts.
        seen: Set of already seen layouts to avoid circular dependencies.
        
    Returns:
        A dictionary mapping key names to their keysym groups.
    """
    if seen is None:
        seen = set()

    if layout_name in seen:
        return {} # Avoid circular dependencies
    seen.add(layout_name)

    if layout_name not in all_layouts:
        # This might be a system layout like "us(base)". For now, we'll ignore them.
        # A more robust solution would be to parse system XKB files as well.
        print(f'Warning: Layout "{layout_name}" not found in the current file. Skipping.', file=sys.stderr)
        return {}

    layout_info = all_layouts[layout_name]
    final_key_map = {}

    # First, apply keys from included layouts (recursively)
    for include_str in layout_info.get('includes', []):
        # The include format can be complex, e.g., "kt(accented_qwerty)"
        # We'll extract the core name for now.
        match = re.match(r'[^\(]+\(([^\)]+)\)', include_str)
        if match:
            included_name = match.group(1)
            included_keys = resolve_layout(included_name, all_layouts, seen)
            final_key_map.update(included_keys)
        else:
            # Handle simpler includes like "us(base)" or just "br"
            included_keys = resolve_layout(include_str, all_layouts, seen)
            final_key_map.update(included_keys)

    # Then, apply keys from the current layout, overriding any from includes
    final_key_map.update(layout_info.get('keys', {}))

    return final_key_map


def keysym_to_unicode(keysym: str, debug: bool = False) -> str:
    """Convert an XKB keysym to a Unicode character, handling hex codes.
    
    Args:
        keysym: The XKB keysym to convert.
        debug: Whether to print debug information.
        
    Returns:
        The Unicode character corresponding to the keysym, or an empty string if not found.
    """
    # If keysym is already a single character, return it directly
    if len(keysym) == 1:
        return keysym
    
    # Handle hexadecimal Unicode values like "0x0105"
    if keysym.startswith('0x'):
        try:
            code_point = int(keysym[2:], 16)
            return chr(code_point)
        except (ValueError, OverflowError):
            if debug:
                print(f"Warning: Could not convert hex keysym '{keysym}' to Unicode.")
            return ''
    
    # Handle keysyms like "U0105"
    if keysym.startswith('U') and len(keysym) >= 5:
        try:
            code_point = int(keysym[1:], 16)
            return chr(code_point)
        except (ValueError, OverflowError):
            if debug:
                print(f"Warning: Could not convert Unicode keysym '{keysym}' to Unicode.")
            return ''
    
    # Special cases for dead keys and other special characters
    special_keysyms = {
        # Dead keys
        'dead_grave': '`',
        'dead_acute': '´',
        'dead_circumflex': '^',
        'dead_tilde': '~',
        'dead_macron': '¯',
        'dead_breve': '˘',
        'dead_abovedot': '˙',
        'dead_diaeresis': '¨',
        'dead_abovering': '˚',
        'dead_doubleacute': '˝',
        'dead_caron': 'ˇ',
        'dead_cedilla': '¸',
        'dead_ogonek': '˛',
        'dead_iota': 'ͺ',
        'dead_voiced_sound': 'ﾞ',
        'dead_semivoiced_sound': 'ﾟ',
        'dead_belowdot': '.',
        'dead_hook': '̉',
        'dead_horn': '̛',
        'dead_stroke': '/',
        'dead_abovecomma': '̓',
        'dead_abovereversedcomma': '̔',
        'dead_doublegrave': '̏',
        'dead_belowring': '̥',
        'dead_belowmacron': '̱',
        'dead_belowcircumflex': '̭',
        'dead_belowtilde': '̰',
        'dead_belowbreve': '̮',
        'dead_belowdiaeresis': '̤',
        'dead_invertedbreve': '̑',
        'dead_belowcomma': '̦',
        'dead_currency': '¤',
        'dead_greek': '',  # No direct equivalent
        
        # Special characters
        'nobreakspace': '\u00A0',  # Non-breaking space
        'space': ' ',
        'exclam': '!',
        'quotedbl': '"',
        'numbersign': '#',
        'dollar': '$',
        'percent': '%',
        'ampersand': '&',
        'apostrophe': "'",
        'parenleft': '(',
        'parenright': ')',
        'asterisk': '*',
        'plus': '+',
        'comma': ',',
        'minus': '-',
        'period': '.',
        'slash': '/',
        'colon': ':',
        'semicolon': ';',
        'less': '<',
        'equal': '=',
        'greater': '>',
        'question': '?',
        'at': '@',
        'bracketleft': '[',
        'backslash': '\\',
        'bracketright': ']',
        'asciicircum': '^',
        'underscore': '_',
        'grave': '`',
        'braceleft': '{',
        'bar': '|',
        'braceright': '}',
        'asciitilde': '~',
        
        # Control keys (these don't produce output in macOS)
        'Return': '',
        'Escape': '',
        'BackSpace': '',
        'Tab': '',
        'Delete': '',
        'Home': '',
        'End': '',
        'Page_Up': '',
        'Page_Down': '',
        'Up': '',
        'Down': '',
        'Left': '',
        'Right': '',
        'Caps_Lock': '',
        'Shift_L': '',
        'Shift_R': '',
        'Control_L': '',
        'Control_R': '',
        'Alt_L': '',
        'Alt_R': '',
        'Meta_L': '',
        'Meta_R': '',
        'Super_L': '',
        'Super_R': '',
        'Hyper_L': '',
        'Hyper_R': '',
        'ISO_Level3_Shift': '',  # AltGr
    }
    
    if keysym in special_keysyms:
        return special_keysyms[keysym]
    
    # Use the generated keysym map
    if keysym in KEYSYM_MAP:
        return KEYSYM_MAP[keysym]
    
    if debug:
        print(f"Warning: Unknown keysym '{keysym}'")
    
    return ''


def generate_macos_layout(layout_name: str, key_map: Dict[str, List[List[str]]], 
                         debug: bool = False) -> str:
    """Generate the .keylayout XML file content.
    
    Args:
        layout_name: The name of the layout.
        key_map: Dictionary mapping key names to their keysym groups.
        debug: Whether to print debug information.
        
    Returns:
        The path to the generated .keylayout file.
    """
    # Create the root element
    root = ET.Element('keyboard', group='126', id='', name=layout_name)
    
    # Add layouts element
    layouts = ET.SubElement(root, 'layouts')
    ET.SubElement(layouts, 'layout', first='0', last='0', mapSet='ANSI', modifiers='modifiers')
    
    # Add modifiers element
    modifiers = ET.SubElement(root, 'modifierMap', id='modifiers', defaultIndex='0')
    
    # Add modifier sets
    modifier_set_0 = ET.SubElement(modifiers, 'keyMapSelect', mapIndex='0')
    ET.SubElement(modifier_set_0, 'modifier', keys='')
    
    modifier_set_1 = ET.SubElement(modifiers, 'keyMapSelect', mapIndex='1')
    ET.SubElement(modifier_set_1, 'modifier', keys='anyShift')
    
    modifier_set_2 = ET.SubElement(modifiers, 'keyMapSelect', mapIndex='2')
    ET.SubElement(modifier_set_2, 'modifier', keys='anyOption')
    
    modifier_set_3 = ET.SubElement(modifiers, 'keyMapSelect', mapIndex='3')
    ET.SubElement(modifier_set_3, 'modifier', keys='anyShift anyOption')
    
    # Add keyMapSet element
    key_map_set = ET.SubElement(root, 'keyMapSet', id='ANSI')
    
    # Add keyMaps for each modifier state
    key_map_0 = ET.SubElement(key_map_set, 'keyMap', index='0')  # No modifier
    key_map_1 = ET.SubElement(key_map_set, 'keyMap', index='1')  # Shift
    key_map_2 = ET.SubElement(key_map_set, 'keyMap', index='2')  # Option
    key_map_3 = ET.SubElement(key_map_set, 'keyMap', index='3')  # Shift+Option
    
    # Add actions element
    actions = ET.SubElement(root, 'actions')
    
    # Track unmapped keysyms for debugging
    unmapped_count = 0
    unmapped_keysyms = []
    
    # Process each key in the key map
    for xkb_key, groups in key_map.items():
        if xkb_key not in XKB_TO_MACOS_KEYCODE:
            if debug:
                print(f"Warning: No macOS keycode mapping for XKB key '{xkb_key}'")
            continue
        
        macos_code = XKB_TO_MACOS_KEYCODE[xkb_key]
        
        # Add key elements to each keyMap
        key_0 = ET.SubElement(key_map_0, 'key', code=str(macos_code))
        key_1 = ET.SubElement(key_map_1, 'key', code=str(macos_code))
        key_2 = ET.SubElement(key_map_2, 'key', code=str(macos_code))
        key_3 = ET.SubElement(key_map_3, 'key', code=str(macos_code))
        
        # State 0: No modifier
        # State 1: Shift
        # State 2: Option
        # State 3: Shift+Option
        # ... and so on for Caps Lock, etc.

        if len(groups) > 0 and len(groups[0]) > 0:
            # No modifier
            keysym = groups[0][0]
            output = keysym_to_unicode(keysym, debug)
            if output == '':
                unmapped_count += 1
                if debug:
                    unmapped_keysyms.append((xkb_key, keysym, 'No modifier'))
            ET.SubElement(key_0, 'action', id=f'k{macos_code}_0').set('output', output)

        if len(groups) > 0 and len(groups[0]) > 1:
            # Shift
            keysym = groups[0][1]
            output = keysym_to_unicode(keysym, debug)
            if output == '':
                unmapped_count += 1
                if debug:
                    unmapped_keysyms.append((xkb_key, keysym, 'Shift'))
            ET.SubElement(key_1, 'action', id=f'k{macos_code}_1').set('output', output)
        
        if len(groups) > 0 and len(groups[0]) > 2:
            # Option (AltGr)
            keysym = groups[0][2]
            output = keysym_to_unicode(keysym, debug)
            if output == '':
                unmapped_count += 1
                if debug:
                    unmapped_keysyms.append((xkb_key, keysym, 'Option'))
            ET.SubElement(key_2, 'action', id=f'k{macos_code}_2').set('output', output)

        if len(groups) > 0 and len(groups[0]) > 3:
            # Shift+Option
            keysym = groups[0][3]
            output = keysym_to_unicode(keysym, debug)
            if output == '':
                unmapped_count += 1
                if debug:
                    unmapped_keysyms.append((xkb_key, keysym, 'Shift+Option'))
            ET.SubElement(key_3, 'action', id=f'k{macos_code}_3').set('output', output)

    # Pretty print the XML
    xml_str = ET.tostring(root, 'utf-8')
    pretty_xml_str = minidom.parseString(xml_str).toprettyxml(indent='    ')

    # Write to file
    output_filename = f'{layout_name}.keylayout'
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write(pretty_xml_str)
    
    if debug and unmapped_count > 0:
        print(f"Warning: {unmapped_count} keysyms could not be mapped to Unicode characters:")
        for xkb_key, keysym, modifier in unmapped_keysyms:
            print(f"  - XKB key: {xkb_key}, Keysym: {keysym}, Modifier: {modifier}")
    
    print(f'Successfully generated {output_filename}')
    return output_filename
