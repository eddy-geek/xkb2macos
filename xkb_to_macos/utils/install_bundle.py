#!/usr/bin/env python3
"""
Install macOS keyboard layout bundles.

This script creates a properly structured .bundle from a .keylayout file
and installs it to the appropriate system location.
"""

import argparse
import plistlib
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Optional

# Import icon conversion functionality
try:
    from generate_icons import png_to_icns
except ImportError:
    # If running as standalone script, try to import from same directory
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "generate_icons",
        Path(__file__).parent / "generate_icons.py"
    )
    if spec and spec.loader:
        generate_icons = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(generate_icons)
        png_to_icns = generate_icons.png_to_icns
    else:
        png_to_icns = None


def convert_icon_if_needed(icon_path: Path) -> Path:
    """
    Convert PNG icon to ICNS if needed.
    
    Args:
        icon_path: Path to icon file (.png or .icns)
    
    Returns:
        Path to .icns file (either original or converted)
    
    Raises:
        ValueError: If icon format is not supported or conversion fails
    """
    if icon_path.suffix.lower() == '.icns':
        # Already ICNS, return as-is
        return icon_path
    
    if icon_path.suffix.lower() == '.png':
        # Convert PNG to ICNS
        if png_to_icns is None:
            raise ValueError(
                "PNG to ICNS conversion not available. "
                "Please convert your PNG to ICNS manually using generate_icons.py"
            )
        
        print(f"Converting PNG to ICNS: {icon_path.name}")
        icns_path = icon_path.with_suffix('.icns')
        
        if png_to_icns(icon_path, icns_path):
            print(f"✓ Converted to: {icns_path}")
            return icns_path
        else:
            raise ValueError(f"Failed to convert {icon_path} to ICNS format")
    
    raise ValueError(
        f"Unsupported icon format: {icon_path.suffix}. "
        "Please provide a .png or .icns file."
    )


def create_bundle_info_plist(
    bundle_id: str,
    bundle_name: str,
    layout_name: str,
    language: str = "en-US",
    version: str = "1.0"
) -> dict:
    """
    Create Info.plist dictionary for keyboard layout bundle.
    
    Args:
        bundle_id: Reverse-DNS bundle identifier (e.g., com.example.keyboardlayout.mylayout)
        bundle_name: Human-readable bundle name
        layout_name: Name of the keyboard layout (must match .keylayout filename without extension)
        language: BCP 47 language code (e.g., en-US, fr-FR, de-DE)
        version: Bundle version string
    
    Returns:
        Dictionary suitable for writing as Info.plist
    """
    # Ensure bundle_id contains .keyboardlayout.
    if '.keyboardlayout.' not in bundle_id:
        parts = bundle_id.split('.')
        if len(parts) >= 2:
            bundle_id = f"{parts[0]}.{parts[1]}.keyboardlayout.{'.'.join(parts[2:])}"
        else:
            bundle_id = f"com.custom.keyboardlayout.{bundle_id}"
    
    # Construct TISInputSourceID
    tis_id = f"{bundle_id}.{layout_name.lower().replace(' ', '')}"
    
    plist_dict = {
        'CFBundleIdentifier': bundle_id,
        'CFBundleName': bundle_name,
        'CFBundleVersion': version,
        f'KLInfo_{layout_name}': {
            'TISInputSourceID': tis_id,
            'TISIntendedLanguage': language,
        }
    }
    
    return plist_dict


def create_bundle(
    keylayout_path: Path,
    output_dir: Path,
    bundle_name: str,
    bundle_id: Optional[str] = None,
    icon_path: Optional[Path] = None,
    language: str = "en-US",
    version: str = "1.0"
) -> Path:
    """
    Create a keyboard layout bundle from a .keylayout file.
    
    Args:
        keylayout_path: Path to the .keylayout file
        output_dir: Directory where the bundle will be created
        bundle_name: Name for the bundle (without .bundle extension)
        bundle_id: Optional custom bundle identifier
        icon_path: Optional path to icon file (.png or .icns, PNG will be auto-converted)
        language: BCP 47 language code
        version: Bundle version
    
    Returns:
        Path to the created bundle
    """
    if not keylayout_path.exists():
        raise FileNotFoundError(f"Keylayout file not found: {keylayout_path}")
    
    # Extract layout name from keylayout file
    layout_name = keylayout_path.stem
    
    # Generate bundle ID if not provided
    if bundle_id is None:
        bundle_id = f"com.custom.keyboardlayout.{layout_name.lower().replace(' ', '_')}"
    
    # Create bundle structure
    bundle_path = output_dir / f"{bundle_name}.bundle"
    contents_path = bundle_path / "Contents"
    resources_path = contents_path / "Resources"
    
    # Parse language code to create .lproj directory
    # Format: language_REGION.lproj (e.g., en_US.lproj, fr_FR.lproj)
    if '-' in language:
        lang, region = language.split('-', 1)
        lproj_name = f"{lang}_{region}.lproj"
    else:
        lproj_name = f"{language}.lproj"
    
    lproj_path = resources_path / lproj_name
    
    # Remove existing bundle if present
    if bundle_path.exists():
        print(f"Removing existing bundle: {bundle_path}")
        shutil.rmtree(bundle_path)
    
    # Create directory structure
    lproj_path.mkdir(parents=True, exist_ok=True)
    
    # Copy keylayout file
    dest_keylayout = lproj_path / keylayout_path.name
    shutil.copy2(keylayout_path, dest_keylayout)
    print(f"✓ Copied keylayout: {dest_keylayout.relative_to(bundle_path)}")
    
    # Handle icon if provided
    if icon_path:
        if not icon_path.exists():
            print(f"⚠ Warning: Icon file not found: {icon_path}")
        else:
            try:
                # Convert PNG to ICNS if needed
                icns_path = convert_icon_if_needed(icon_path)
                
                # Copy the ICNS file to bundle
                dest_icon = resources_path / icns_path.name
                shutil.copy2(icns_path, dest_icon)
                print(f"✓ Copied icon: {dest_icon.relative_to(bundle_path)}")
            except ValueError as e:
                print(f"⚠ Warning: {e}")
    
    # Create Info.plist
    plist_dict = create_bundle_info_plist(
        bundle_id=bundle_id,
        bundle_name=bundle_name,
        layout_name=layout_name,
        language=language,
        version=version
    )
    
    plist_path = contents_path / "Info.plist"
    with open(plist_path, 'wb') as f:
        plistlib.dump(plist_dict, f)
    print(f"✓ Created Info.plist")
    
    print(f"\n✓ Bundle created: {bundle_path}")
    print(f"  Bundle ID: {bundle_id}")
    print(f"  Layout: {layout_name}")
    print(f"  Language: {language}")
    
    return bundle_path


def install_bundle(bundle_path: Path, user_install: bool = False) -> bool:
    """
    Install keyboard layout bundle to system or user directory.
    
    Args:
        bundle_path: Path to the .bundle to install
        user_install: If True, install to ~/Library; if False, install to /Library (requires sudo)
    
    Returns:
        True if installation succeeded
    """
    if not bundle_path.exists():
        raise FileNotFoundError(f"Bundle not found: {bundle_path}")
    
    # Determine installation directory
    if user_install:
        install_dir = Path.home() / "Library" / "Keyboard Layouts"
        print(f"\nInstalling to user directory: {install_dir}")
        print("⚠ Note: User installations may have compatibility issues with some applications.")
        print("   Consider using system installation (without --user) for better reliability.")
    else:
        install_dir = Path("/Library/Keyboard Layouts")
        print(f"\nInstalling to system directory: {install_dir}")
    
    # Create installation directory if it doesn't exist
    if not install_dir.exists():
        if user_install:
            install_dir.mkdir(parents=True, exist_ok=True)
        else:
            print(f"Creating directory (requires sudo): {install_dir}")
            subprocess.run(['sudo', 'mkdir', '-p', str(install_dir)], check=True)
    
    dest_path = install_dir / bundle_path.name
    
    # Remove existing bundle if present
    if dest_path.exists():
        print(f"Removing existing bundle: {dest_path}")
        if user_install:
            shutil.rmtree(dest_path)
        else:
            subprocess.run(['sudo', 'rm', '-rf', str(dest_path)], check=True)
    
    # Copy bundle to installation directory
    if user_install:
        shutil.copytree(bundle_path, dest_path)
    else:
        print("Copying bundle (requires sudo)...")
        subprocess.run(['sudo', 'cp', '-R', str(bundle_path), str(dest_path)], check=True)
    
    print(f"✓ Installed: {dest_path}")
    
    # Flush plist cache to help with detection
    try:
        plist_path = Path.home() / "Library" / "Preferences" / "com.apple.HIToolbox.plist"
        subprocess.run(
            ['defaults', 'read', str(plist_path), 'dummy'],
            capture_output=True,
            check=False
        )
    except Exception:
        pass
    
    return True


def print_post_install_instructions(bundle_name: str, user_install: bool):
    """Print instructions for activating the keyboard layout."""
    print("\n" + "="*70)
    print("Installation Complete!")
    print("="*70)
    print("\nNext steps:")
    print("1. Log out and log back in (or restart your Mac)")
    print("2. Open System Preferences/Settings > Keyboard > Input Sources")
    print("3. Click the '+' button")
    print("4. Look for your layout under 'Others' or search for it")
    print(f"5. Select '{bundle_name}' and click 'Add'")
    print("\nTroubleshooting:")
    print("- If the layout doesn't appear, try restarting your Mac")
    print("- If it appears but won't activate, try removing and re-adding it")
    
    if user_install:
        print("- If issues persist, try system installation without --user flag")
    
    print("\nTo uninstall:")
    if user_install:
        print(f"  rm -rf ~/Library/Keyboard\\ Layouts/{bundle_name}.bundle")
    else:
        print(f"  sudo rm -rf /Library/Keyboard\\ Layouts/{bundle_name}.bundle")
    print("="*70)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Create and install macOS keyboard layout bundles",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Install with default settings (requires sudo)
  %(prog)s my_layout.keylayout
  
  # Install to user directory (no sudo required, but less reliable)
  %(prog)s --user my_layout.keylayout
  
  # Install with custom icon (PNG or ICNS)
  %(prog)s --icon icons/my_icon.png my_layout.keylayout
  %(prog)s --icon icons/my_icon.icns my_layout.keylayout
  
  # Full customization
  %(prog)s --name "My Custom Layout" \\
           --bundle-id com.example.keyboardlayout.custom \\
           --icon icons/custom.png \\
           --language fr-FR \\
           my_layout.keylayout
  
  # Just create bundle without installing
  %(prog)s --no-install --output ./bundles my_layout.keylayout
        """
    )
    
    parser.add_argument('keylayout', type=Path, help='.keylayout file path')
    parser.add_argument('--name', help='Bundle name (default: derived from keylayout filename)')
    parser.add_argument('--bundle-id', help='Bundle ID (default: auto-generated)')
    parser.add_argument('--icon', type=Path, help='Icon file (.png or .icns). PNG -> ICNS conversion')
    parser.add_argument('--language', default='en-US', help='Language code (default: en-US)')
    parser.add_argument('--version', default='1.0', help='Bundle version (default: 1.0)')
    parser.add_argument('--output', type=Path, help='Bundle output dir (default: same as keylayout file)')
    parser.add_argument('--user', action='store_true', help='Install to ~/Library/Keyboard Layouts')
    parser.add_argument('--no-install', action='store_true', help='Create bundle without installation')
    
    args = parser.parse_args()
    
    # Validate keylayout file
    if not args.keylayout.exists():
        print(f"Error: Keylayout file not found: {args.keylayout}", file=sys.stderr)
        return 1
    
    if args.keylayout.suffix != '.keylayout':
        print(f"Error: File must have .keylayout extension: {args.keylayout}", file=sys.stderr)
        return 1
    
    # Determine bundle name
    bundle_name = args.name or args.keylayout.stem
    
    # Determine output directory
    output_dir = args.output or args.keylayout.parent
    output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # Create bundle
        print(f"Creating bundle for: {args.keylayout.name}")
        print(f"Bundle name: {bundle_name}")
        
        bundle_path = create_bundle(
            keylayout_path=args.keylayout,
            output_dir=output_dir,
            bundle_name=bundle_name,
            bundle_id=args.bundle_id,
            icon_path=args.icon,
            language=args.language,
            version=args.version
        )
        
        # Install bundle unless --no-install specified
        if not args.no_install:
            install_bundle(bundle_path, user_install=args.user)
            print_post_install_instructions(bundle_name, args.user)
        else:
            print(f"\n✓ Bundle created (not installed): {bundle_path}")
            print(f"\nTo install manually:")
            if args.user:
                print(f"  cp -R {bundle_path} ~/Library/Keyboard\\ Layouts/")
            else:
                print(f"  sudo cp -R {bundle_path} /Library/Keyboard\\ Layouts/")
        
        return 0
        
    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
