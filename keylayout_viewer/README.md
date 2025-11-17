# Keylayout SVG Viewer

Intelligent visualization tool for macOS `.keylayout` files.

## Quick Start

```bash
python keylayout_viewer.py input.keylayout [output.svg]
```

## Features

### 🎯 Smart Layer Optimization
- Automatically hides predictable A-Z mappings (a→A)
- Shows only modifiers that produce actual output
- Minimal visual clutter, maximum information

### 🎨 Visual Design
- Color-coded modifier states
- Dead key markers with combining diacritics (◌́, ◌̈, ◌̃)
- Dynamic legend showing only used modifiers

### 🖱️ Interactive (Optional)
- Hover tooltips with Unicode codepoints
- Click to expand complex keys
- Badge indicators for hidden layers

## Example Output

**Typical key display:**
```
┌─────────────┐
│   ⁄         │  Shift+Option: ⁄
│             │
│ ¡   1       │  Option: ¡, Base: 1
│             │
│   !         │  Shift: !
└─────────────┘
```

**Letter key (optimized):**
```
┌─────────────┐
│   Å         │  Shift+Option: Å
│             │
│ å           │  Option: å
│             │  (base a, shift A hidden)
└─────────────┘
```

## Modes

- `--mode minimal`: Base + Shift + Option only (default)
- `--mode full`: All 8 modifier layers
- `--interactive`: Add JavaScript tooltips/modals
- `--diff old.keylayout new.keylayout`: Compare layouts

## See Also

- [SPECS.md](./SPECS.md) - Complete implementation specification
- [../docs/keylayout-spec.md](../docs/keylayout-spec.md) - macOS keylayout format reference
