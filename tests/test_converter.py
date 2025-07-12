#!/usr/bin/env python3
"""Tests for the XKB to macOS layout converter."""

import os
import sys
import unittest
from pathlib import Path

from xkb_to_macos.core.converter import (
    parse_xkb_symbols_file,
    resolve_layout,
    keysym_to_unicode,
    generate_macos_layout,
)


class TestXKBConverter(unittest.TestCase):
    """Test cases for the XKB to macOS layout converter."""

    def setUp(self):
        """Set up test fixtures."""
        self.project_root = Path(__file__).parent.parent
        self.test_data_dir = self.project_root / "tests" / "data"
        self.package_data_dir = self.project_root / "xkb_to_macos" / "data"
        
        # Copy the test file to the test data directory if it doesn't exist
        if not (self.test_data_dir / "kt.symbols.xkb").exists():
            os.makedirs(self.test_data_dir, exist_ok=True)
            if (self.package_data_dir / "kt.symbols.xkb").exists():
                import shutil
                shutil.copy(
                    self.package_data_dir / "kt.symbols.xkb",
                    self.test_data_dir / "kt.symbols.xkb"
                )
        
        self.test_file = str(self.test_data_dir / "kt.symbols.xkb")
    
    def test_parse_xkb_symbols_file(self):
        """Test that the parser correctly extracts layout blocks."""
        layouts = parse_xkb_symbols_file(self.test_file)
        self.assertGreater(len(layouts), 0, "Should parse at least one layout block")
        
        # Check that the 'dev' layout exists
        self.assertIn('dev', layouts, "Should find the 'dev' layout")
        
        # Check that the layout has both keys and includes
        dev_layout = layouts['dev']
        self.assertIn('keys', dev_layout, "Layout should have 'keys' dictionary")
        self.assertIn('includes', dev_layout, "Layout should have 'includes' list")
    
    def test_resolve_layout(self):
        """Test that layout resolution correctly handles includes."""
        layouts = parse_xkb_symbols_file(self.test_file)
        resolved = resolve_layout('dev', layouts)
        
        # Check that we have keys in the resolved layout
        self.assertGreater(len(resolved), 0, "Resolved layout should have keys")
        
        # Check for a few specific keys that should be present
        self.assertIn('AD01', resolved, "Should have key AD01 (Q)")
        self.assertIn('AD02', resolved, "Should have key AD02 (W)")
    
    def test_keysym_to_unicode(self):
        """Test that keysym mapping works correctly."""
        # Test basic character
        self.assertEqual(keysym_to_unicode('a'), 'a', "Should map 'a' to 'a'")
        
        # Test special keysym
        self.assertEqual(keysym_to_unicode('eacute'), 'é', "Should map 'eacute' to 'é'")
        
        # Test hex code
        self.assertEqual(keysym_to_unicode('0x00e9'), 'é', "Should map '0x00e9' to 'é'")
    
    def test_us_mac_conversion(self):
        """Test conversion of us-mac.symbols.xkb file and validate output format."""
        # Path to the us-mac symbols file
        us_mac_file = str(self.project_root / "data" / "us-mac.symbols.xkb")
        
        # Skip test if file doesn't exist
        if not Path(us_mac_file).exists():
            self.skipTest(f"Test file {us_mac_file} not found")
        
        # Parse the XKB symbols file
        layouts = parse_xkb_symbols_file(us_mac_file)
        self.assertGreater(len(layouts), 0, "Should parse at least one layout block")
        self.assertIn('mac', layouts, "Should find the 'mac' layout")
        
        # Resolve the layout
        final_map = resolve_layout('mac', layouts)
        self.assertGreater(len(final_map), 0, "Resolved layout should have keys")
        
        # Validate specific keys are present
        expected_keys = ['TLDE', 'AE01', 'AE02', 'AD01', 'AD02', 'AC01', 'AB01']
        for key in expected_keys:
            self.assertIn(key, final_map, f"Should have key {key}")
        
        # Check that keys have the expected 4-level structure (base, shift, option, shift+option)
        for key, mappings in final_map.items():
            self.assertEqual(len(mappings), 1, f"Key {key} should have one mapping group")
            key_levels = mappings[0]
            self.assertEqual(len(key_levels), 4, f"Key {key} should have 4 levels (base, shift, option, shift+option)")
        
        # Test specific key mappings to validate XKB parsing
        tlde_mapping = final_map['TLDE'][0]
        self.assertEqual(tlde_mapping[0], 'grave', "TLDE base level should be 'grave'")
        self.assertEqual(tlde_mapping[1], 'asciitilde', "TLDE shift level should be 'asciitilde'")
        
        # Count unmapped keysyms (known issue)
        unmapped_keysyms = []
        for key, mappings in final_map.items():
            for level_group in mappings:
                for keysym in level_group:
                    if keysym_to_unicode(keysym) == keysym and len(keysym) > 1:
                        # This is likely an unmapped keysym
                        unmapped_keysyms.append((key, keysym))
        
        # Verify that all keysyms are now properly mapped (should be zero unmapped)
        self.assertEqual(len(unmapped_keysyms), 0, 
                        f"Expected zero unmapped keysyms, but found {len(unmapped_keysyms)}: {[keysym for _, keysym in unmapped_keysyms]}")
        
        # Generate the macOS layout (this tests the full conversion pipeline)
        import tempfile
        import os
        import sys
        from io import StringIO
        
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            # Capture stdout to check for warnings
            captured_output = StringIO()
            original_stdout = sys.stdout
            try:
                os.chdir(temp_dir)
                sys.stdout = captured_output
                output_file = generate_macos_layout('mac', final_map, debug=True)
                sys.stdout = original_stdout
                
                # Check that the file was generated
                self.assertTrue(os.path.exists(output_file), "Should generate output file")
                
                # Check for keycode mapping warnings
                output_text = captured_output.getvalue()
                keycode_warnings = [line for line in output_text.split('\n') 
                                  if 'No macOS keycode mapping for XKB key' in line]
                self.assertEqual(len(keycode_warnings), 0, 
                               f"Expected no keycode mapping warnings, but found: {keycode_warnings}")
                
                # Read and validate the generated XML structure
                with open(output_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Basic XML structure validation
                self.assertIn('<?xml version="1.0" ?>', content, "Should have XML declaration")
                self.assertIn('<keyboard', content, "Should have keyboard element")
                self.assertIn('<modifierMap', content, "Should have modifierMap element")
                self.assertIn('<keyMapSet', content, "Should have keyMapSet element")
                
                # Validate modifier structure (current implementation has 4 levels)
                self.assertIn('mapIndex="0"', content, "Should have base modifier map")
                self.assertIn('mapIndex="1"', content, "Should have shift modifier map")
                self.assertIn('mapIndex="2"', content, "Should have option modifier map")
                self.assertIn('mapIndex="3"', content, "Should have shift+option modifier map")
                
                # Check for proper modifier key definitions
                self.assertIn('keys=""', content, "Should have empty keys for base level")
                self.assertIn('keys="anyShift"', content, "Should have anyShift modifier")
                self.assertIn('keys="anyOption"', content, "Should have anyOption modifier")
                self.assertIn('keys="anyShift anyOption"', content, "Should have combined shift+option modifier")
                
            finally:
                sys.stdout = original_stdout
                os.chdir(original_cwd)
        
        # Document findings for improvement
        print(f"\n=== US-Mac Conversion Test Results ===")
        print(f"Total keys parsed: {len(final_map)}")
        print(f"Unmapped keysyms found: {len(unmapped_keysyms)}")
        if unmapped_keysyms:
            print("Sample unmapped keysyms:")
            for key, keysym in unmapped_keysyms[:5]:
                print(f"  - Key {key}: {keysym}")
        print(f"Generated layout file successfully")
        print(f"Current modifier structure: 4-level (base, shift, option, shift+option)")
        print(f"Reference structure: 8-level (with caps, command, control support)")


if __name__ == '__main__':
    unittest.main()
