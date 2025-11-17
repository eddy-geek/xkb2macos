#!/usr/bin/env python3
"""
Keylayout SVG Viewer - Intelligent visualization for macOS .keylayout files
"""

import argparse
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict


# macOS virtual key codes to physical positions (x, y, width, height in px)
# Standard key: 50x50, spacing: 5px
KEY_POSITIONS = {
    # Row 1 (number row)
    50: (0, 0, 50, 50),      # `
    18: (55, 0, 50, 50),     # 1
    19: (110, 0, 50, 50),    # 2
    20: (165, 0, 50, 50),    # 3
    21: (220, 0, 50, 50),    # 4
    23: (275, 0, 50, 50),    # 5
    22: (330, 0, 50, 50),    # 6
    26: (385, 0, 50, 50),    # 7
    28: (440, 0, 50, 50),    # 8
    25: (495, 0, 50, 50),    # 9
    29: (550, 0, 50, 50),    # 0
    27: (605, 0, 50, 50),    # -
    24: (660, 0, 50, 50),    # =
    51: (715, 0, 100, 50),   # Backspace
    
    # Row 2 (QWERTY)
    48: (0, 55, 75, 50),     # Tab
    12: (80, 55, 50, 50),    # Q
    13: (135, 55, 50, 50),   # W
    14: (190, 55, 50, 50),   # E
    15: (245, 55, 50, 50),   # R
    17: (300, 55, 50, 50),   # T
    16: (355, 55, 50, 50),   # Y
    32: (410, 55, 50, 50),   # U
    34: (465, 55, 50, 50),   # I
    31: (520, 55, 50, 50),   # O
    35: (575, 55, 50, 50),   # P
    33: (630, 55, 50, 50),   # [
    30: (685, 55, 50, 50),   # ]
    42: (740, 55, 75, 50),   # \
    
    # Row 3 (ASDF)
    57: (0, 110, 85, 50),    # Caps Lock
    0: (90, 110, 50, 50),    # A
    1: (145, 110, 50, 50),   # S
    2: (200, 110, 50, 50),   # D
    3: (255, 110, 50, 50),   # F
    5: (310, 110, 50, 50),   # G
    4: (365, 110, 50, 50),   # H
    38: (420, 110, 50, 50),  # J
    40: (475, 110, 50, 50),  # K
    37: (530, 110, 50, 50),  # L
    41: (585, 110, 50, 50),  # ;
    39: (640, 110, 50, 50),  # '
    36: (695, 110, 120, 50), # Return
    
    # Row 4 (ZXCV)
    56: (0, 165, 105, 50),   # Left Shift
    6: (110, 165, 50, 50),   # Z
    7: (165, 165, 50, 50),   # X
    8: (220, 165, 50, 50),   # C
    9: (275, 165, 50, 50),   # V
    11: (330, 165, 50, 50),  # B
    45: (385, 165, 50, 50),  # N
    46: (440, 165, 50, 50),  # M
    43: (495, 165, 50, 50),  # ,
    47: (550, 165, 50, 50),  # .
    44: (605, 165, 50, 50),  # /
    # Right Shift at 660, 165, 155, 50 (not mapped as modifier key)
    
    # Row 5 (space bar)
    49: (200, 220, 350, 50), # Space
}

# Letter keys (A-Z) for predictable mapping detection
LETTER_KEYS = {0, 1, 2, 3, 5, 4, 38, 40, 37, 41, 6, 7, 8, 9, 11, 45, 46, 12, 13, 14, 15, 17, 16, 32, 34, 31, 35}

# Modifier state colors
MODIFIER_COLORS = {
    'base': '#000000',           # Black
    'shift': '#0066CC',          # Blue
    'option': '#009900',         # Green
    'shift+option': '#CC6600',   # Orange
    'caps': '#666666',           # Gray
    'command': '#990099',        # Purple
    'option+command': '#CC0066', # Magenta
    'control': '#999999',        # Light gray
}

# Modifier symbols
MODIFIER_SYMBOLS = {
    'shift': '⇧',
    'option': '⌥',
    'command': '⌘',
    'control': '⌃',
    'caps': '⇪',
}


@dataclass
class OptimizedOutput:
    """Optimized key output with minimal visible layers"""
    visible_layers: Dict[str, Tuple[str, str]]  # position -> (state, char)
    hidden_count: int = 0
    is_predictable: bool = False
    is_dead_key: bool = False
    all_outputs: Dict[str, str] = field(default_factory=dict)


@dataclass
class KeyboardLayout:
    """Parsed keyboard layout data"""
    name: str
    key_outputs: Dict[int, Dict[str, str]]  # keycode -> state -> character
    modifier_states: List[str]
    dead_keys: Dict[int, str] = field(default_factory=dict)


class KeylayoutParser:
    """Parse macOS .keylayout XML files"""
    
    def __init__(self, filepath: Path):
        self.filepath = filepath
        # Read and clean the XML to handle invalid character references
        content = filepath.read_text(encoding='utf-8')
        # Remove problematic control character references
        import re
        # Replace control characters (0x00-0x1F except tab, newline, carriage return)
        # and 0x7F (DEL) with empty strings as they're invalid in XML
        content = re.sub(r'&#x00[0-8];', '', content)  # 0x00-0x08
        content = re.sub(r'&#x000[BC];', '', content)  # 0x0B-0x0C
        content = re.sub(r'&#x00[0-1][0-9A-F];', '', content)  # 0x00-0x1F
        content = re.sub(r'&#x007F;', '', content)  # DEL
        
        # Parse the cleaned XML
        self.root = ET.fromstring(content)
    
    def parse_file(self) -> KeyboardLayout:
        """Parse the keylayout file and extract all data"""
        name = self.root.get('name', 'Unknown Layout')
        key_outputs = self.extract_key_outputs()
        modifier_states = self.extract_modifier_states(key_outputs)
        dead_keys = self.detect_dead_keys(key_outputs)
        
        return KeyboardLayout(
            name=name,
            key_outputs=key_outputs,
            modifier_states=modifier_states,
            dead_keys=dead_keys
        )
    
    def extract_key_outputs(self) -> Dict[int, Dict[str, str]]:
        """Extract all key outputs for different modifier states"""
        outputs = defaultdict(dict)
        
        # Find all keyMap elements (standard structure)
        for keymap in self.root.findall('.//keyMap'):
            index = int(keymap.get('index', 0))
            state_name = self._index_to_state(index)
            
            for key in keymap.findall('key'):
                code = int(key.get('code'))
                
                # Try direct output attribute
                output = key.get('output')
                if output:
                    outputs[code][state_name] = output
                    continue
                
                # Try action element
                action = key.find('action')
                if action is not None:
                    action_output = action.get('output')
                    if action_output:
                        outputs[code][state_name] = action_output
        
        # Also handle alternative structure where keys are directly in keyMapSet
        # with multiple action elements per key (dev-dead-keys.keylayout format)
        for keymapset in self.root.findall('.//keyMapSet'):
            for key in keymapset.findall('key'):
                code = int(key.get('code'))
                
                # Each action represents a different modifier state
                for i, action in enumerate(key.findall('action')):
                    state_name = self._index_to_state(i)
                    action_output = action.get('output')
                    if action_output:
                        outputs[code][state_name] = action_output
        
        return dict(outputs)
    
    def _index_to_state(self, index: int) -> str:
        """Map keyMap index to modifier state name"""
        # Standard mapping (may vary by layout)
        mapping = {
            0: 'base',
            1: 'shift',
            2: 'option',
            3: 'shift+option',
            4: 'command',
            5: 'shift+command',
            6: 'option+command',
            7: 'control',
        }
        return mapping.get(index, f'state_{index}')
    
    def extract_modifier_states(self, key_outputs: Dict[int, Dict[str, str]]) -> List[str]:
        """Get list of all modifier states present in the layout"""
        states = set()
        for outputs in key_outputs.values():
            states.update(outputs.keys())
        
        # Return in standard order
        order = ['base', 'shift', 'option', 'shift+option', 'caps', 
                 'command', 'shift+command', 'option+command', 'control']
        return [s for s in order if s in states]
    
    def detect_dead_keys(self, key_outputs: Dict[int, Dict[str, str]]) -> Dict[int, str]:
        """Detect dead keys (combining diacritics)"""
        dead_keys = {}
        
        # Look for combining diacritical marks (Unicode range U+0300-U+036F)
        for keycode, outputs in key_outputs.items():
            for state, char in outputs.items():
                if char and len(char) == 1:
                    codepoint = ord(char)
                    # Combining diacritical marks
                    if 0x0300 <= codepoint <= 0x036F:
                        dead_keys[keycode] = char
                        break
                    # Common dead key characters
                    if char in ['´', '`', '^', '~', '¨', '¸', '˚', 'ˇ', '¯', '˘', '˙', '˝', '˛']:
                        dead_keys[keycode] = char
                        break
        
        return dead_keys


class OutputOptimizer:
    """Optimize key outputs for minimal display"""
    
    @staticmethod
    def analyze_key(keycode: int, outputs: Dict[str, str]) -> OptimizedOutput:
        """Analyze and optimize outputs for a single key"""
        classification = OutputOptimizer._classify_key(keycode, outputs)
        visible = OutputOptimizer._get_visible_layers(keycode, outputs, classification)
        hidden_count = len(outputs) - len(visible)
        
        return OptimizedOutput(
            visible_layers=visible,
            hidden_count=hidden_count,
            is_predictable=(classification == 'PREDICTABLE_LETTER'),
            is_dead_key=(classification == 'DEAD_KEY'),
            all_outputs=outputs.copy()
        )
    
    @staticmethod
    def _classify_key(keycode: int, outputs: Dict[str, str]) -> str:
        """Classify key type for optimization"""
        # Check if all outputs are identical first
        unique_outputs = set(o for o in outputs.values() if o)
        if len(unique_outputs) <= 1:
            return 'UNIFORM'
        
        # Check if it's a letter key (A-Z)
        if keycode in LETTER_KEYS:
            base = outputs.get('base', '')
            shift = outputs.get('shift', '')
            # If base is lowercase and shift is uppercase of same letter
            if base and shift and base.lower() == shift.lower() == base:
                return 'PREDICTABLE_LETTER'
        
        # Check for dead keys (combining marks)
        for output in outputs.values():
            if output and len(output) == 1:
                codepoint = ord(output)
                if 0x0300 <= codepoint <= 0x036F:
                    return 'DEAD_KEY'
                if output in ['´', '`', '^', '~', '¨', '¸', '˚', 'ˇ', '¯', '˘', '˙', '˝', '˛']:
                    return 'DEAD_KEY'
        
        return 'NORMAL'
    
    @staticmethod
    def _get_visible_layers(keycode: int, outputs: Dict[str, str], 
                           classification: str) -> Dict[str, Tuple[str, str]]:
        """Determine which layers should be visible"""
        visible = {}
        
        if classification == 'PREDICTABLE_LETTER':
            # Hide lower-case variant
            for state, char in outputs.items():
                if state not in ['base'] and char:
                    visible[state] = (state, char)
        
        elif classification == 'UNIFORM':
            for state, char in outputs.items():
                visible['base'] = (state, char)
                break
        
        elif classification == 'DEAD_KEY':
            # Show all dead key states with special formatting
            for state, char in outputs.items():
                if char:
                    # Format with dotted circle for combining marks
                    if len(char) == 1 and 0x0300 <= ord(char) <= 0x036F:
                        visible[state] = (state, f'◌{char}')
                    else:
                        visible[state] = (state, char)
        
        else:  # NORMAL
            # Show all distinct outputs
            base_output = outputs.get('base', '')
            for state, char in outputs.items():
                if char and (char != base_output or state == 'base'):
                    # For non-letter keys, always show base
                    if keycode not in LETTER_KEYS or state != 'base':
                        visible[state] = (state, char)
                    elif state == 'base' and char:
                        visible[state] = (state, char)
        print(keycode, classification, visible)
        return visible
    
    @staticmethod
    def get_used_modifiers(layout: KeyboardLayout) -> Set[str]:
        """Get set of modifiers that actually produce output"""
        active = set()
        for outputs in layout.key_outputs.values():
            for state, char in outputs.items():
                if char:  # Non-empty output
                    active.add(state)
        return active


class SVGRenderer:
    """Render keyboard layout as SVG"""
    
    def __init__(self, layout: KeyboardLayout, interactive: bool = False):
        self.layout = layout
        self.interactive = interactive
        self.width = 850
        self.height = 350
        self.svg_parts = []
    
    def render(self) -> str:
        """Generate complete SVG"""
        self._add_header()
        self._add_styles()
        self._render_keyboard()
        self._add_legend()
        if self.interactive:
            self._add_interactive_script()
        self._add_footer()
        
        return '\n'.join(self.svg_parts)
    
    def _add_header(self):
        """Add SVG header"""
        self.svg_parts.append(f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" 
     viewBox="0 0 {self.width} {self.height}" 
     width="{self.width}" height="{self.height}">
<title>{self._escape_xml(self.layout.name)}</title>''')
    
    def _add_styles(self):
        """Add embedded CSS styles"""
        self.svg_parts.append('''
<defs>
  <style type="text/css">
    <![CDATA[
      .key-rect { fill: white; stroke: #333; stroke-width: 1; }
      .key-text { font-family: "SF Mono", Monaco, monospace; font-size: 12px; }
      .key-text-small { font-family: "SF Mono", Monaco, monospace; font-size: 10px; }
      .dead-key { stroke: #CC0000; stroke-dasharray: 3,3; stroke-width: 2; }
      .badge { fill: #FFD700; font-size: 10px; font-weight: bold; }
      .legend-text { font-family: "SF Mono", Monaco, monospace; font-size: 11px; }
    ]]>
  </style>
</defs>''')
    
    def _render_keyboard(self):
        """Render all keys"""
        self.svg_parts.append('<g id="keyboard" transform="translate(10, 10)">')
        
        for keycode, position in KEY_POSITIONS.items():
            if keycode in self.layout.key_outputs:
                outputs = self.layout.key_outputs[keycode]
                optimized = OutputOptimizer.analyze_key(keycode, outputs)
                self._render_key(keycode, position, optimized)
        
        self.svg_parts.append('</g>')
    
    def _render_key(self, keycode: int, position: Tuple[int, int, int, int], 
                    optimized: OptimizedOutput):
        """Render a single key with its outputs"""
        x, y, w, h = position
        
        # Key rectangle
        rect_class = 'key-rect dead-key' if optimized.is_dead_key else 'key-rect'
        self.svg_parts.append(f'<g id="key_{keycode}">')
        self.svg_parts.append(f'  <rect x="{x}" y="{y}" width="{w}" height="{h}" class="{rect_class}"/>')
        
        # Add tooltip with all outputs
        if self.interactive:
            tooltip = self._generate_tooltip(keycode, optimized)
            self.svg_parts.append(f'  <title>{self._escape_xml(tooltip)}</title>')
        
        # Render visible characters
        self._render_characters(x, y, w, h, optimized.visible_layers)
        
        # Add badge if there are hidden layers
        if optimized.hidden_count > 0:
            self.svg_parts.append(f'  <text x="{x + w - 8}" y="{y + 12}" class="badge">★</text>')
        
        self.svg_parts.append('</g>')
    
    def _render_characters(self, x: int, y: int, w: int, h: int, 
                          visible_layers: Dict[str, Tuple[str, str]]):
        """Render characters at appropriate positions within key"""
        # Position mapping: state -> (x_offset, y_offset)
        positions = {
            'base': (w * 0.6, h * 0.6),           # Center-right
            'shift': (w * 0.6, h * 0.85),         # Bottom-right
            'option': (w * 0.2, h * 0.6),         # Center-left
            'shift+option': (w * 0.8, h * 0.25),  # Top-right
            'caps': (w * 0.2, h * 0.85),          # Bottom-left
            'command': (w * 0.8, h * 0.85),       # Bottom-right-far
            'option+command': (w * 0.8, h * 0.6), # Center-right-far
            'control': (w * 0.9, h * 0.25),       # Top-right-far
        }
        
        for state, (state_name, char) in visible_layers.items():
            if state in positions:
                offset_x, offset_y = positions[state]
                color = MODIFIER_COLORS.get(state, '#000000')
                
                # Escape XML special characters
                char_escaped = self._escape_xml(char)
                
                self.svg_parts.append(
                    f'  <text x="{x + offset_x}" y="{y + offset_y}" '
                    f'class="key-text" fill="{color}" text-anchor="middle">'
                    f'{char_escaped}</text>'
                )
    
    def _generate_tooltip(self, keycode: int, optimized: OptimizedOutput) -> str:
        """Generate tooltip text for a key"""
        lines = [f'Key code: {keycode}']
        
        for state in ['base', 'shift', 'option', 'shift+option', 'command', 'control']:
            if state in optimized.all_outputs:
                char = optimized.all_outputs[state]
                if char:
                    symbol = MODIFIER_SYMBOLS.get(state.split('+')[0], '')
                    codepoint = f'U+{ord(char):04X}' if len(char) == 1 else ''
                    lines.append(f'{symbol} {state}: {char} {codepoint}')
        
        if optimized.is_dead_key:
            lines.append('(Dead key - combines with next character)')
        
        return '\n'.join(lines)
    
    def _add_legend(self):
        """Add legend showing modifier colors and dead keys"""
        used_modifiers = OutputOptimizer.get_used_modifiers(self.layout)
        
        self.svg_parts.append('<g id="legend" transform="translate(10, 290)">')
        self.svg_parts.append('  <text x="0" y="0" class="legend-text" font-weight="bold">Legend:</text>')
        
        x_offset = 0
        y_offset = 15
        
        # Modifier colors
        for state in ['base', 'shift', 'option', 'shift+option', 'command', 'control']:
            if state in used_modifiers:
                color = MODIFIER_COLORS[state]
                symbol = ' '.join(MODIFIER_SYMBOLS.get(s, s) for s in state.split('+'))
                
                self.svg_parts.append(f'  <circle cx="{x_offset + 5}" cy="{y_offset - 3}" r="4" fill="{color}"/>')
                self.svg_parts.append(f'  <text x="{x_offset + 12}" y="{y_offset}" class="legend-text">{symbol} {state}</text>')
                
                x_offset += 120
                if x_offset > 600:
                    x_offset = 0
                    y_offset += 15
        
        # Dead keys
        if self.layout.dead_keys:
            y_offset += 20
            dead_key_list = ', '.join(f'◌{char}' for char in set(self.layout.dead_keys.values()))
            self.svg_parts.append(f'  <text x="0" y="{y_offset}" class="legend-text">Dead keys: {dead_key_list}</text>')
        
        self.svg_parts.append('</g>')
    
    def _add_interactive_script(self):
        """Add JavaScript for interactive features"""
        # Placeholder for future JavaScript interactivity
        pass
    
    def _add_footer(self):
        """Add SVG footer"""
        self.svg_parts.append('</svg>')
    
    @staticmethod
    def _escape_xml(text: str) -> str:
        """Escape XML special characters"""
        return (text.replace('&', '&amp;')
                   .replace('<', '&lt;')
                   .replace('>', '&gt;')
                   .replace('"', '&quot;')
                   .replace("'", '&apos;'))
    
    def save(self, filepath: Path):
        """Save SVG to file"""
        svg_content = self.render()
        filepath.write_text(svg_content, encoding='utf-8')


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Generate SVG visualization of macOS keylayout files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s layout.keylayout
  %(prog)s layout.keylayout output.svg
  %(prog)s layout.keylayout --interactive
        '''
    )
    
    parser.add_argument('input', type=Path, help='Input .keylayout file')
    parser.add_argument('output', type=Path, nargs='?', help='Output .svg file (default: input_layout.svg)')
    parser.add_argument('--interactive', action='store_true', help='Add interactive tooltips')
    parser.add_argument('--mode', choices=['minimal', 'full'], default='minimal',
                       help='Display mode (default: minimal)')
    
    args = parser.parse_args()
    
    # Validate input
    if not args.input.exists():
        print(f"Error: Input file not found: {args.input}", file=sys.stderr)
        return 1
    
    # Determine output path
    if args.output is None:
        args.output = args.input.parent / f"{args.input.stem}_layout.svg"
    
    try:
        # Parse keylayout
        print(f"Parsing {args.input}...")
        parser_obj = KeylayoutParser(args.input)
        layout = parser_obj.parse_file()
        
        print(f"Layout: {layout.name}")
        print(f"Keys: {len(layout.key_outputs)}")
        print(f"Modifiers: {', '.join(layout.modifier_states)}")
        print(f"Dead keys: {len(layout.dead_keys)}")
        
        # Render SVG
        print(f"Rendering SVG...")
        renderer = SVGRenderer(layout, interactive=args.interactive)
        renderer.save(args.output)
        
        print(f"✓ Saved to {args.output}")
        return 0
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
