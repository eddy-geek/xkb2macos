#!/usr/bin/env python3
"""
Tests for keylayout_viewer.py
"""

import pytest
from pathlib import Path
import tempfile
import xml.etree.ElementTree as ET
from keylayout_viewer import (
    KeylayoutParser, OutputOptimizer, SVGRenderer,
    KeyboardLayout, OptimizedOutput, LETTER_KEYS
)


@pytest.fixture
def simple_keylayout_xml():
    """Create a simple test keylayout XML"""
    return '''<?xml version="1.0" encoding="UTF-8"?>
<keyboard group="126" id="-1" name="Test Layout" maxout="1">
    <layouts>
        <layout first="0" last="17" mapSet="ANSI" modifiers="modifiers"/>
    </layouts>
    <keyMapSet id="ANSI">
        <keyMap index="0">
            <key code="0" output="a"/>
            <key code="1" output="s"/>
            <key code="18" output="1"/>
        </keyMap>
        <keyMap index="1">
            <key code="0" output="A"/>
            <key code="1" output="S"/>
            <key code="18" output="!"/>
        </keyMap>
        <keyMap index="2">
            <key code="0" output="å"/>
            <key code="1" output="ß"/>
            <key code="18" output="¡"/>
        </keyMap>
        <keyMap index="3">
            <key code="0" output="Å"/>
            <key code="1" output="Í"/>
            <key code="18" output="⁄"/>
        </keyMap>
    </keyMapSet>
</keyboard>'''


@pytest.fixture
def dead_key_layout_xml():
    """Create a keylayout with dead keys"""
    return '''<?xml version="1.0" encoding="UTF-8"?>
<keyboard group="126" id="-1" name="Dead Key Layout" maxout="1">
    <layouts>
        <layout first="0" last="17" mapSet="ANSI" modifiers="modifiers"/>
    </layouts>
    <keyMapSet id="ANSI">
        <keyMap index="0">
            <key code="14" output="e"/>
        </keyMap>
        <keyMap index="1">
            <key code="14" output="E"/>
        </keyMap>
        <keyMap index="2">
            <key code="14" output="´"/>
        </keyMap>
        <keyMap index="3">
            <key code="14" output="̋"/>
        </keyMap>
    </keyMapSet>
</keyboard>'''


@pytest.fixture
def temp_keylayout_file(simple_keylayout_xml):
    """Create a temporary keylayout file"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.keylayout', delete=False) as f:
        f.write(simple_keylayout_xml)
        temp_path = Path(f.name)
    yield temp_path
    temp_path.unlink()


class TestKeylayoutParser:
    """Test KeylayoutParser class"""
    
    def test_parse_simple_layout(self, temp_keylayout_file):
        """Test parsing a simple layout"""
        parser = KeylayoutParser(temp_keylayout_file)
        layout = parser.parse_file()
        
        assert layout.name == "Test Layout"
        assert len(layout.key_outputs) == 3
        assert 0 in layout.key_outputs
        assert layout.key_outputs[0]['base'] == 'a'
        assert layout.key_outputs[0]['shift'] == 'A'
    
    def test_extract_key_outputs(self, temp_keylayout_file):
        """Test key output extraction"""
        parser = KeylayoutParser(temp_keylayout_file)
        outputs = parser.extract_key_outputs()
        
        # Check key 0 (A)
        assert outputs[0]['base'] == 'a'
        assert outputs[0]['shift'] == 'A'
        assert outputs[0]['option'] == 'å'
        assert outputs[0]['shift+option'] == 'Å'
        
        # Check key 18 (1)
        assert outputs[18]['base'] == '1'
        assert outputs[18]['shift'] == '!'
        assert outputs[18]['option'] == '¡'
    
    def test_index_to_state_mapping(self, temp_keylayout_file):
        """Test modifier index to state name mapping"""
        parser = KeylayoutParser(temp_keylayout_file)
        
        assert parser._index_to_state(0) == 'base'
        assert parser._index_to_state(1) == 'shift'
        assert parser._index_to_state(2) == 'option'
        assert parser._index_to_state(3) == 'shift+option'
    
    def test_detect_dead_keys(self):
        """Test dead key detection"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.keylayout', delete=False) as f:
            f.write('''<?xml version="1.0" encoding="UTF-8"?>
<keyboard group="126" id="-1" name="Dead Key Test">
    <keyMapSet id="ANSI">
        <keyMap index="2">
            <key code="14" output="´"/>
            <key code="15" output="̋"/>
        </keyMap>
    </keyMapSet>
</keyboard>''')
            temp_path = Path(f.name)
        
        try:
            parser = KeylayoutParser(temp_path)
            layout = parser.parse_file()
            
            # Check that dead keys are detected
            assert len(layout.dead_keys) > 0
        finally:
            temp_path.unlink()
    
    def test_extract_modifier_states(self, temp_keylayout_file):
        """Test extraction of used modifier states"""
        parser = KeylayoutParser(temp_keylayout_file)
        layout = parser.parse_file()
        
        assert 'base' in layout.modifier_states
        assert 'shift' in layout.modifier_states
        assert 'option' in layout.modifier_states
        assert 'shift+option' in layout.modifier_states


class TestOutputOptimizer:
    """Test OutputOptimizer class"""
    
    def test_classify_predictable_letter(self):
        """Test classification of predictable letter keys"""
        outputs = {'base': 'a', 'shift': 'A'}
        classification = OutputOptimizer._classify_key(0, outputs)  # 0 = A key
        
        assert classification == 'PREDICTABLE_LETTER'
    
    def test_classify_normal_key(self):
        """Test classification of normal keys"""
        outputs = {'base': '1', 'shift': '!', 'option': '¡'}
        classification = OutputOptimizer._classify_key(18, outputs)  # 18 = 1 key
        
        assert classification == 'NORMAL'
    
    def test_classify_dead_key(self):
        """Test classification of dead keys"""
        outputs = {'base': 'e', 'option': '´'}
        classification = OutputOptimizer._classify_key(14, outputs)
        
        assert classification == 'DEAD_KEY'
    
    def test_classify_uniform_key(self):
        """Test classification of uniform keys"""
        outputs = {'base': 'x', 'shift': 'x', 'option': 'x'}
        classification = OutputOptimizer._classify_key(7, outputs)
        
        assert classification == 'UNIFORM'
    
    def test_optimize_predictable_letter(self):
        """Test optimization of predictable letter keys"""
        outputs = {'base': 'a', 'shift': 'A', 'option': 'å', 'shift+option': 'Å'}
        optimized = OutputOptimizer.analyze_key(0, outputs)
        
        # Should hide base but show shift (uppercase) and option layers
        assert optimized.is_predictable
        assert 'base' not in optimized.visible_layers
        assert 'shift' in optimized.visible_layers
        assert 'option' in optimized.visible_layers
        assert 'shift+option' in optimized.visible_layers
    
    def test_optimize_normal_key(self):
        """Test optimization of normal keys"""
        outputs = {'base': '1', 'shift': '!', 'option': '¡', 'shift+option': '⁄'}
        optimized = OutputOptimizer.analyze_key(18, outputs)
        
        # Should show all layers for non-letter keys
        assert not optimized.is_predictable
        assert len(optimized.visible_layers) > 0
    
    def test_optimize_uniform_key(self):
        """Test optimization of uniform keys"""
        outputs = {'base': 'x', 'shift': 'x', 'option': 'x'}
        optimized = OutputOptimizer.analyze_key(7, outputs)
        
        # Should show nothing for uniform outputs
        assert len(optimized.visible_layers) == 0
    
    def test_optimize_dead_key(self):
        """Test optimization of dead keys"""
        outputs = {'base': 'e', 'option': '´', 'shift+option': '̋'}
        optimized = OutputOptimizer.analyze_key(14, outputs)
        
        assert optimized.is_dead_key
        # Dead keys should be formatted with dotted circle
        if 'shift+option' in optimized.visible_layers:
            _, char = optimized.visible_layers['shift+option']
            assert '◌' in char or char == '̋'
    
    def test_hidden_count(self):
        """Test hidden layer counting"""
        outputs = {'base': 'a', 'shift': 'A', 'option': 'å', 'shift+option': 'Å'}
        optimized = OutputOptimizer.analyze_key(0, outputs)
        
        # Should hide only base layer (1 hidden)
        assert optimized.hidden_count == 1
    
    def test_get_used_modifiers(self):
        """Test detection of used modifiers"""
        layout = KeyboardLayout(
            name="Test",
            key_outputs={
                0: {'base': 'a', 'shift': 'A', 'option': 'å'},
                18: {'base': '1', 'shift': '!'}
            },
            modifier_states=['base', 'shift', 'option']
        )
        
        used = OutputOptimizer.get_used_modifiers(layout)
        
        assert 'base' in used
        assert 'shift' in used
        assert 'option' in used
        assert 'command' not in used


class TestSVGRenderer:
    """Test SVGRenderer class"""
    
    def test_render_creates_svg(self, temp_keylayout_file):
        """Test that rendering creates valid SVG"""
        parser = KeylayoutParser(temp_keylayout_file)
        layout = parser.parse_file()
        
        renderer = SVGRenderer(layout, interactive=False)
        svg = renderer.render()
        
        assert svg.startswith('<?xml version="1.0"')
        assert '<svg' in svg
        assert '</svg>' in svg
        assert layout.name in svg
    
    def test_render_with_interactive(self, temp_keylayout_file):
        """Test rendering with interactive features"""
        parser = KeylayoutParser(temp_keylayout_file)
        layout = parser.parse_file()
        
        renderer = SVGRenderer(layout, interactive=True)
        svg = renderer.render()
        
        assert '<title>' in svg  # Tooltips should be present
    
    def test_save_to_file(self, temp_keylayout_file):
        """Test saving SVG to file"""
        parser = KeylayoutParser(temp_keylayout_file)
        layout = parser.parse_file()
        
        renderer = SVGRenderer(layout)
        
        with tempfile.NamedTemporaryFile(suffix='.svg', delete=False) as f:
            output_path = Path(f.name)
        
        try:
            renderer.save(output_path)
            assert output_path.exists()
            
            content = output_path.read_text()
            assert '<svg' in content
            assert '</svg>' in content
        finally:
            output_path.unlink()
    
    def test_escape_xml(self):
        """Test XML escaping"""
        assert SVGRenderer._escape_xml('<test>') == '&lt;test&gt;'
        assert SVGRenderer._escape_xml('a & b') == 'a &amp; b'
        assert SVGRenderer._escape_xml('"quote"') == '&quot;quote&quot;'
    
    def test_legend_includes_used_modifiers(self, temp_keylayout_file):
        """Test that legend only shows used modifiers"""
        parser = KeylayoutParser(temp_keylayout_file)
        layout = parser.parse_file()
        
        renderer = SVGRenderer(layout)
        svg = renderer.render()
        
        # Should include base, shift, option
        assert 'base' in svg.lower()
        assert 'shift' in svg.lower() or '⇧' in svg
        assert 'option' in svg.lower() or '⌥' in svg
    
    def test_dead_key_visualization(self):
        """Test dead key visualization in SVG"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.keylayout', delete=False) as f:
            f.write('''<?xml version="1.0" encoding="UTF-8"?>
<keyboard group="126" id="-1" name="Dead Key Test">
    <keyMapSet id="ANSI">
        <keyMap index="0">
            <key code="14" output="e"/>
        </keyMap>
        <keyMap index="2">
            <key code="14" output="´"/>
        </keyMap>
    </keyMapSet>
</keyboard>''')
            temp_path = Path(f.name)
        
        try:
            parser = KeylayoutParser(temp_path)
            layout = parser.parse_file()
            
            renderer = SVGRenderer(layout)
            svg = renderer.render()
            
            # Should have dead key styling
            assert 'dead-key' in svg or 'Dead key' in svg
        finally:
            temp_path.unlink()


class TestIntegration:
    """Integration tests"""
    
    def test_full_pipeline(self, temp_keylayout_file):
        """Test complete pipeline from parsing to SVG generation"""
        # Parse
        parser = KeylayoutParser(temp_keylayout_file)
        layout = parser.parse_file()
        
        assert layout.name == "Test Layout"
        assert len(layout.key_outputs) > 0
        
        # Optimize
        for keycode, outputs in layout.key_outputs.items():
            optimized = OutputOptimizer.analyze_key(keycode, outputs)
            assert isinstance(optimized, OptimizedOutput)
        
        # Render
        renderer = SVGRenderer(layout)
        svg = renderer.render()
        
        assert len(svg) > 0
        assert '<svg' in svg
        
        # Save
        with tempfile.NamedTemporaryFile(suffix='.svg', delete=False) as f:
            output_path = Path(f.name)
        
        try:
            renderer.save(output_path)
            assert output_path.exists()
            assert output_path.stat().st_size > 0
        finally:
            output_path.unlink()
    
    def test_real_layout_file(self):
        """Test with actual dev.keylayout file if it exists"""
        test_file = Path(__file__).parent.parent / 'data' / 'output' / 'dev.keylayout'
        
        if not test_file.exists():
            pytest.skip(f"Test file not found: {test_file}")
        
        parser = KeylayoutParser(test_file)
        layout = parser.parse_file()
        
        assert len(layout.key_outputs) > 0
        
        renderer = SVGRenderer(layout, interactive=True)
        svg = renderer.render()
        
        assert '<svg' in svg
        assert len(svg) > 1000  # Should be substantial


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
