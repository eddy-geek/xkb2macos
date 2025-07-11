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


if __name__ == '__main__':
    unittest.main()
