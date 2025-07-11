"""Mapping utilities for XKB to macOS layout conversion.

This module contains the mapping from XKB key names and keysyms to macOS equivalents.
"""
from typing import Dict, Optional


# A mapping from XKB key names to macOS virtual key codes.
# Sources:
# - https://www.x.org/releases/X11R7.6/doc/xorg-docs/input/XKB-PROT.html#_keyboard_geometry
# - https://gist.github.com/eegrok/949034
XKB_TO_MACOS_KEYCODE: Dict[str, int] = {
    # Alphanumeric keys
    'TLDE': 50,  # Tilde (`)
    'AE01': 18,  # 1
    'AE02': 19,  # 2
    'AE03': 20,  # 3
    'AE04': 21,  # 4
    'AE05': 23,  # 5
    'AE06': 22,  # 6
    'AE07': 26,  # 7
    'AE08': 28,  # 8
    'AE09': 25,  # 9
    'AE10': 29,  # 0
    'AE11': 27,  # Minus (-)
    'AE12': 24,  # Equal (=)

    'AD01': 12,  # Q
    'AD02': 13,  # W
    'AD03': 14,  # E
    'AD04': 15,  # R
    'AD05': 17,  # T
    'AD06': 16,  # Y
    'AD07': 32,  # U
    'AD08': 34,  # I
    'AD09': 31,  # O
    'AD10': 35,  # P
    'AD11': 33,  # Left Brace ([)
    'AD12': 30,  # Right Brace (])

    'AC01': 0,   # A
    'AC02': 1,   # S
    'AC03': 2,   # D
    'AC04': 3,   # F
    'AC05': 5,   # G
    'AC06': 4,   # H
    'AC07': 38,  # J
    'AC08': 40,  # K
    'AC09': 37,  # L
    'AC10': 41,  # Semicolon (;)
    'AC11': 39,  # Quote (')

    'AB01': 6,   # Z
    'AB02': 7,   # X
    'AB03': 8,   # C
    'AB04': 9,   # V
    'AB05': 11,  # B
    'AB06': 45,  # N
    'AB07': 46,  # M
    'AB08': 43,  # Comma (,)
    'AB09': 47,  # Period (.)
    'AB10': 44,  # Slash (/)

    # Modifier keys
    'LALT': 58,  # Left Alt (Option)
    'RALT': 61,  # Right Alt (Option)
    'LCTL': 59,  # Left Ctrl
    'RCTL': 62,  # Right Ctrl
    'LFSH': 56,  # Left Shift
    'RTSH': 60,  # Right Shift
    'CAPS': 57,  # Caps Lock

    # Other keys
    'SPCE': 49,  # Space
    'BKSP': 51,  # Backspace (Delete)
    'RTRN': 36,  # Return (Enter)
    'TAB': 48,   # Tab
    'ESC': 53,   # Escape
}


def keysym_to_unicode(keysym: str) -> str:
    """Convert an XKB keysym to a Unicode character.
    
    Args:
        keysym: The XKB keysym to convert.
        
    Returns:
        The Unicode character corresponding to the keysym, or an empty string if not found.
    """
    # This is a placeholder. A real implementation will need a comprehensive mapping.
    # For now, we'll handle basic alphanumeric characters and some common symbols.
    if len(keysym) == 1:
        return keysym

    # A small sample of mappings
    keysym_map = {
        'period': '.', 'comma': ',', 'slash': '/', 'semicolon': ';',
        'apostrophe': "'", 'bracketleft': '[', 'bracketright': ']',
        'minus': '-', 'equal': '=', 'grave': '`',
        'Shift_L': '', 'Shift_R': '', 'Control_L': '', 'Control_R': '',
        'Alt_L': '', 'Alt_R': '', 'Caps_Lock': '', 'space': ' ',
        'Return': '\r', 'BackSpace': '&#x8;', 'Tab': '\t', 'Escape': '&#x1b;'
    }

    return keysym_map.get(keysym, '')
