#!/usr/bin/env python3
"""Generate simple keyboard layout icons."""

import subprocess
from pathlib import Path

def png_to_icns(png_path: Path, icns_path: Path):
    """Convert PNG to ICNS using iconutil."""
    iconset_path = png_path.parent / f"{png_path.stem}.iconset"
    
    try:
        # Create iconset directory
        iconset_path.mkdir(exist_ok=True)
        
        # Generate all required sizes using sips
        sizes = [
            (16, 'icon_16x16.png'),
            (32, 'icon_16x16@2x.png'),
            (32, 'icon_32x32.png'),
            (64, 'icon_32x32@2x.png'),
            (128, 'icon_128x128.png'),
            (256, 'icon_128x128@2x.png'),
            (256, 'icon_256x256.png'),
            (512, 'icon_256x256@2x.png'),
            (512, 'icon_512x512.png'),
            (1024, 'icon_512x512@2x.png'),
        ]
        
        for size, filename in sizes:
            output = iconset_path / filename
            subprocess.run([
                'sips', '-z', str(size), str(size),
                str(png_path), '--out', str(output)
            ], check=True, capture_output=True)
        
        # Convert iconset to icns
        subprocess.run([
            'iconutil', '-c', 'icns', str(iconset_path),
            '-o', str(icns_path)
        ], check=True, capture_output=True)
        
        # Clean up iconset
        subprocess.run(['rm', '-rf', str(iconset_path)], check=True)
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error converting {png_path} to ICNS: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        # Convert provided PNG to ICNS
        png_path = Path(sys.argv[1])
        if not png_path.exists():
            print(f"Error: {png_path} not found")
            sys.exit(1)
        
        icns_path = png_path.with_suffix('.icns')
        print(f"Converting {png_path} to {icns_path}...")
        
        if png_to_icns(png_path, icns_path):
            print(f"✓ Created: {icns_path}")
        else:
            print("✗ Conversion failed")
            sys.exit(1)
    else:
        print("\nTo create an ICNS file from your PNG:")
        print("  python3 generate_icons.py your_icon.png")