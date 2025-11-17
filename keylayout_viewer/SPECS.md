# Keylayout SVG Viewer - Implementation Specifications

## Objective
Create a Python script that parses macOS `.keylayout` XML files and generates an **intelligent, minimal SVG visualization** of the keyboard layout showing character outputs for different modifier combinations.

## Key Innovations
1. **Smart Layer Optimization:** Automatically hide predictable outputs (A→a, A+Shift→A) to reduce visual clutter
2. **Adaptive Display:** Show only the modifier combinations that actually produce characters
3. **Interactive SVG:** Hover tooltips with Unicode details, optional click-to-expand for complex keys
4. **Dead Key Visualization:** Special markers (◌́) and legend for combining diacritics
5. **Dynamic Legend:** Only show modifiers actually used in the layout

## Input
- Path to a `.keylayout` XML file (macOS keyboard layout format)
- Optional: Output SVG filename (default: `{input_name}_layout.svg`)
- Optional: Mode flags (minimal/full/interactive/diff)

## Core Requirements

### 1. XML Parsing
- Parse the `.keylayout` XML structure focusing on:
  - `<keyMap>` elements with different `index` values (modifier states)
  - `<key>` elements with `code` and `output`/`action` attributes
  - `<action>` elements for complex key behaviors (if present)
  - `<modifierMap>` to understand modifier combinations

### 2. Key Code Mapping
Map macOS virtual key codes to physical key positions on US ANSI layout:

```
Physical Layout (ASCII representation):
┌───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬─────────┐
│ ` │ 1 │ 2 │ 3 │ 4 │ 5 │ 6 │ 7 │ 8 │ 9 │ 0 │ - │ = │ Backsp  │
├───┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬───────┤
│ Tab │ Q │ W │ E │ R │ T │ Y │ U │ I │ O │ P │ [ │ ] │   \   │
├─────┴┬──┴┬──┴┬──┴┬──┴┬──┴┬──┴┬──┴┬──┴┬──┴┬──┴┬──┴┬──┴───────┤
│ Caps │ A │ S │ D │ F │ G │ H │ J │ K │ L │ ; │ ' │  Return  │
├──────┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴──────────┤
│ Shift  │ Z │ X │ C │ V │ B │ N │ M │ , │ . │ / │   Shift    │
├────┬───┴┬──┴─┬─┴───┴───┴───┴───┴───┴──┬┴───┼───┴┬────┬──────┤
│Ctrl│ Opt│Cmd │         Space          │Cmd │Opt │Menu│ Ctrl │
└────┴────┴────┴────────────────────────┴────┴────┴────┴──────┘

Key Code Reference (critical mappings):
Row 1: 50,18,19,20,21,23,22,26,28,25,29,27,24,51
Row 2: 48,12,13,14,15,17,16,32,34,31,35,33,30,42
Row 3: 57,0,1,2,3,5,4,38,40,37,41,39,36
Row 4: 56,6,7,8,9,11,45,46,43,47,44,56
Row 5: 59,58,55,49,55,58,110,59
```

### 3. SVG Generation

#### Key Dimensions
- Standard key: 50x50px
- Key spacing: 5px
- Special key widths:
  - Tab: 75px
  - Caps Lock: 85px
  - Shift: 105px (left), 125px (right)
  - Backspace: 100px
  - Return: 100px
  - Space: 350px
  - Modifiers: 65px

#### Character Placement Strategy

**Adaptive Layout:** Minimize displayed layers by analyzing actual key outputs:

1. **Detect unique values** across all modifier states per key
2. **Skip redundant layers:**
   - Omit lowercase A-Z on base layer (implied by key label)
   - Omit uppercase A-Z on shift layer (predictable)
   - Hide layers where output = base output (no change)
   - Collapse Command/Control layers if they don't produce characters

3. **Typical 4-layer layout** (most common):
```
┌─────────────┐
│   Shift+Opt │  Top-right: Shift+Option (orange)
│             │
│ Opt   Base  │  Left: Option (green), Right: Base (black)
│             │
│   Shift     │  Bottom-right: Shift (blue)
└─────────────┘
```

4. **Extended layout** (when needed):
```
┌─────────────┐
│ S+O+C   Cmd │  Top: Shift+Opt+Cmd, Command
│             │
│ S+O   Base  │  Middle: Shift+Option, Base
│             │
│ Opt   Shift │  Bottom: Option, Shift
└─────────────┘
```

5. **Position priority** (use only what's needed):
   - Position 1 (center): Base (if non-obvious)
   - Position 2 (bottom-right): Shift (if differs from base)
   - Position 3 (left): Option
   - Position 4 (top-right): Shift+Option
   - Position 5+ (adaptive): Other modifiers only if they produce output

#### Visual Design
- **Colors by modifier state:**
  - Base (no modifier): #000000 (black)
  - Shift: #0066CC (blue)
  - Option: #009900 (green)
  - Shift+Option: #CC6600 (orange)
  - Caps Lock: #666666 (gray)
  - Command: #990099 (purple)
  - Option+Command: #CC0066 (magenta)
  - Control/other: #999999 (light gray)

- **Font specifications:**
  - Size: 12px for regular chars, 10px for combining marks
  - Family: "SF Mono", "Monaco", monospace
  - Weight: normal (bold for active modifiers in legend)

#### Interactive Features (SVG Advanced)

1. **Hover tooltips** (`<title>` elements):
   - Show full modifier combination name
   - Display Unicode codepoint (U+XXXX)
   - For dead keys: preview available combinations

2. **Click/tap expansion** (JavaScript optional):
   - Click key to show modal with all 8 layers in table format
   - Useful for keys with many modifiers or dead key sequences

3. **Visual indicators:**
   - Small badge (e.g., "★") on keys with hidden layers
   - Dead key marker (red dashed border + "◌" symbol)
   - Dim/fade unused modifier keys in bottom row

#### Legend (Dynamic)
Position below keyboard, **only showing modifiers actually used** in the layout:
- Color swatches with modifier symbols: ⇧ Shift, ⌥ Option, ⌘ Command, ⌃ Control, ⇪ Caps
- Example minimal: "⇧ Shift (blue) • ⌥ Option (green) • ⇧⌥ Shift+Option (orange)"
- Example extended: Add Command/Control only if they produce characters
- Dead key legend: List all dead keys with their base character (e.g., "◌́ = acute accent")

### 4. Layer Optimization Algorithm

**Goal:** Show minimum information needed to understand the layout.

**Step 1: Classify each key**
```python
def classify_key(keycode, outputs):
    # Check if it's a letter key (A-Z)
    if keycode in LETTER_KEYS:
        base = outputs.get('base', '')
        shift = outputs.get('shift', '')
        # If base is lowercase and shift is uppercase of same letter
        if base.lower() == shift.lower() == base:
            return 'PREDICTABLE_LETTER'
    
    # Check if all outputs are identical
    unique_outputs = set(outputs.values())
    if len(unique_outputs) == 1:
        return 'UNIFORM'
    
    # Check for dead keys
    if any(is_dead_key(output) for output in outputs.values()):
        return 'DEAD_KEY'
    
    return 'NORMAL'
```

**Step 2: Determine visible layers per key**
```python
def get_visible_layers(keycode, outputs, classification):
    visible = {}
    
    if classification == 'PREDICTABLE_LETTER':
        # Only show non-letter outputs (Option, Shift+Option, etc.)
        for state, char in outputs.items():
            if state not in ['base', 'shift'] and char:
                visible[state] = char
    
    elif classification == 'UNIFORM':
        # Show nothing if all outputs are the same
        pass
    
    elif classification == 'DEAD_KEY':
        # Show all dead key states with special formatting
        for state, char in outputs.items():
            if is_dead_key(char):
                visible[state] = format_dead_key(char)  # e.g., "◌́"
    
    else:  # NORMAL
        # Show all distinct outputs
        for state, char in outputs.items():
            if char and char != outputs.get('base'):
                visible[state] = char
        # Always show base if it's not a letter
        if outputs.get('base') and keycode not in LETTER_KEYS:
            visible['base'] = outputs['base']
    
    return visible
```

**Step 3: Global modifier detection**
```python
def get_active_modifiers(layout):
    """Only include modifiers in legend if they produce output somewhere"""
    active = set()
    for keycode, outputs in layout.items():
        for state, char in outputs.items():
            if char:  # Non-empty output
                active.add(state)
    return active
```

### 5. Decision Points

#### Character Rendering
- **Unicode handling:** Use direct UTF-8
- **Combining marks:** Position above base character with adjusted spacing
- **Control chars:** Show symbol  and Unicode name (e.g., "TAB", "ESC") 
- **Missing outputs:** Leave position empty

#### Layout Variations
- **Dead keys:** Mark with special border (dashed red)
- **Action references:** Follow action ID to find actual output.
- **Multiple outputs:** Show first character only with "..." indicator
 - If it's a dead key with many non standard values, use a joker and use the legend smartly.

#### Error Handling
- **Invalid key codes:** Skip or show error marker
- **Malformed XML:** Graceful degradation with partial output
- **Missing modifier maps:** Use default 4-state (base, shift, opt, shift+opt)

### 6. Implementation Structure

```python
class KeylayoutParser:
    def parse_file(path) -> KeyboardLayout
    def extract_modifier_maps() -> List[ModifierState]
    def extract_key_outputs() -> Dict[keycode, Dict[state, char]]
    def detect_dead_keys() -> Dict[keycode, DeadKeyInfo]
    
class OutputOptimizer:
    """Analyzes and minimizes displayed layers"""
    def analyze_key(outputs: Dict[state, char]) -> OptimizedOutput
    def should_skip_layer(key_code, state, output) -> bool
    def get_used_modifiers(layout) -> Set[ModifierState]
    
class SVGRenderer:
    def create_keyboard_base() -> SVGElement
    def render_key(keycode, optimized_outputs, position) -> SVGElement
    def add_tooltips(key_element, full_outputs) -> None
    def add_interactive_layer() -> SVGElement  # Optional JS
    def add_legend(used_modifiers, dead_keys) -> SVGElement
    def save(filename)

class KeyboardLayout:
    key_positions = {...}  # keycode -> (x, y, width, height)
    modifier_states = [...]  # ordered list of states
    key_outputs = {...}  # keycode -> state -> character
    dead_keys = {...}  # keycode -> dead key info
    
class OptimizedOutput:
    visible_layers: Dict[position, (state, char, color)]
    hidden_count: int  # Number of hidden but available layers
    is_predictable: bool  # e.g., A->a, A+Shift->A
```

### 7. Output Format
- SVG 1.1 compliant
- Viewbox: 0 0 800 400 (adjustable)
- Embedded styles (no external CSS)
- UTF-8 encoding with proper XML declaration

### 8. Creative Enhancements

#### A. Smart Layer Collapsing Examples
```
Key 'A' (typical):
  Base: a, Shift: A → Show A
  Option: å, Shift+Option: Å → Show
  
Key '1' (symbol-rich):
  Base: 1, Shift: !, Option: ¡, Shift+Option: ⁄
  → Show all 4 (non-predictable)
  
Key 'E' (with dead key):
  Base: e, Shift: E → Hide
  Option: ´ (dead), Shift+Option: ˝ (dead)
  → Show "◌́" and "◌˝" with dead key marker
```

#### B. Hover Tooltip Content
```xml
<title>
Key: E
Base: e
Shift: E
Option: ´ (dead key - acute accent)
  ´+a → á, ´+e → é, ´+i → í, ...
Shift+Option: ˝ (dead key - double acute)
Unicode: U+0301 (combining acute)
</title>
```

#### C. Interactive Modal (Optional JS)
When clicking a key with "★" badge, show popup:
```
┌─────────────────────────────────┐
│ Key: E (keycode 14)             │
├─────────────────────────────────┤
│ No modifier:        e  (U+0065) │
│ ⇧ Shift:            E  (U+0045) │
│ ⌥ Option:           ´  (U+00B4) │
│   → Dead key: acute accent      │
│   → Combinations: a→á e→é i→í   │
│ ⇧⌥ Shift+Option:    ˝  (U+02DD) │
│   → Dead key: double acute      │
│ ⌘ Command:          [system]    │
└─────────────────────────────────┘
```

#### D. Dead Key Visualization
For keys that trigger dead key states, show:
1. Dashed red border around key
2. Combining diacritic with dotted circle: ◌́ ◌̈ ◌̃
3. In legend: "Dead Keys: ◌́(E+⌥) ◌̈(U+⌥) ◌̃(N+⌥) → combine with next key"

#### E. Diff Mode (Future Enhancement)
Compare two layouts side-by-side:
- Highlight keys that differ in green/red
- Show "before → after" for changed keys
- Useful for testing layout modifications

### 9. Output Modes

Provide CLI flags for different use cases:
```bash
# Minimal: Only base + shift + option (most common)
python keylayout_viewer.py layout.keylayout --mode minimal

# Full: Show all 8 layers (debugging)
python keylayout_viewer.py layout.keylayout --mode full

# Interactive: Include JavaScript for tooltips/modals
python keylayout_viewer.py layout.keylayout --interactive

# Comparison: Diff two layouts
python keylayout_viewer.py old.keylayout new.keylayout --diff
```

### 10. Testing Considerations
- Validate against both simple (dev.keylayout) and complex (English Standard.keylayout) layouts
- Test with layouts having 4, 6, and 8 modifier states
- Verify dead key detection and visualization
- Handle edge cases: empty outputs, undefined keys, special characters
- Ensure visual clarity at different zoom levels

### 11. Example Output Scenarios

**Scenario 1: US English (minimal)**
- Only 2 layers visible per key (base + shift for symbols)
- A-Z keys show nothing (predictable)
- Legend shows only: ⇧ Shift

**Scenario 2: US International (moderate)**
- 4 layers: base, shift, option, shift+option
- Dead keys on ', ", `, ~, ^ with special markers
- Legend shows: ⇧ Shift • ⌥ Option • ⇧⌥ Shift+Option • Dead Keys: ◌́ ◌̈ ◌̀ ◌̃ ◌̂

**Scenario 3: Programmer layout (complex)**
- Heavy use of option layer for symbols
- Some command combinations for special chars
- Badge indicators on keys with 5+ layers
- Interactive mode recommended

## Deliverable
Single Python script `keylayout_viewer.py` with:
- No external dependencies beyond standard library (xml.etree, svg generation)
- Command-line interface with multiple modes
- Smart layer optimization by default
- Optional interactive features (SVG + embedded JS)
- Clear documentation and error messages
- Modular design for easy extension