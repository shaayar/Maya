"""
Build script for creating platform-specific installers for MAYA AI Chatbot.
This script automates the process of creating distributable packages.
"""

import os
import sys
import shutil
import platform
import subprocess
from pathlib import Path
from typing import List, Optional

# Build configuration
APP_NAME = "MAYA AI"
VERSION = "1.0.0"
AUTHOR = "MAYA Development Team"
DESCRIPTION = "A powerful AI assistant with voice and screen interaction capabilities"

# Paths
BASE_DIR = Path(__file__).parent
DIST_DIR = BASE_DIR / "dist"
BUILD_DIR = BASE_DIR / "build"
SPEC_FILE = BASE_DIR / "maya.spec"

# Platform detection
IS_WINDOWS = platform.system() == "Windows"
IS_MAC = platform.system() == "Darwin"
IS_LINUX = platform.system() == "Linux"

def run_command(command: List[str], cwd: Optional[Path] = None) -> bool:
    """Run a shell command and return True if successful."""
    print(f"Running: {' '.join(command)}")
    try:
        subprocess.check_call(command, cwd=cwd or BASE_DIR)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        return False

def clean_build():
    """Clean build artifacts."""
    print("Cleaning build directories...")
    for directory in [BUILD_DIR, DIST_DIR]:
        if directory.exists():
            shutil.rmtree(directory)
    print("Clean complete.")

def install_dependencies():
    """Install build dependencies."""
    print("Installing build dependencies...")
    if IS_WINDOWS:
        run_command(["pip", "install", "pyinstaller", "nsis", "wheel"])
    elif IS_MAC:
        run_command(["pip", "install", "py2app", "wheel"])
    else:  # Linux
        run_command(["pip", "install", "pyinstaller", "wheel"])
    print("Dependencies installed.")

def build_windows():
    """Build Windows installer using PyInstaller and NSIS."""
    print("Building Windows installer...")
    
    # Create executable
    run_command([
        "pyinstaller",
        "--name", APP_NAME,
        "--windowed",
        "--onefile",
        "--icon", str(BASE_DIR / "resources" / "icons" / "maya.ico"),
        "--add-data", f"{BASE_DIR / 'resources'}{os.pathsep}resources",
        str(BASE_DIR / "main.py")
    ])
    
    # Create NSIS installer script
    nsis_script = f"""
    !include "MUI2.nsh"
    
    ; General
    Name "{APP_NAME}"
    OutFile "{DIST_DIR / f'{APP_NAME.replace(" ", "")}-{VERSION}-Setup.exe'}"
    InstallDir "$PROGRAMFILES\\{APP_NAME}"
    
    ; Interface settings
    !define MUI_ABORTWARNING
    
    ; Pages
    !insertmacro MUI_PAGE_DIRECTORY
    !insertmacro MUI_PAGE_INSTFILES
    
    ; Languages
    !insertmacro MUI_LANGUAGE "English"
    
    ; Installer sections
    Section "MainSection" SEC01
        SetOutPath "$INSTDIR"
        SetOverwrite try
        
        ; Add files
        File /r "{DIST_DIR / 'maya'}\\*.*"
        
        ; Create start menu shortcut
        CreateDirectory "$SMPROGRAMS\\{APP_NAME}"
        CreateShortCut "$SMPROGRAMS\\{APP_NAME}\\{APP_NAME}.lnk" "$INSTDIR\\{APP_NAME}.exe"
        
        ; Create desktop shortcut
        CreateShortCut "$DESKTOP\\{APP_NAME}.lnk" "$INSTDIR\\{APP_NAME}.exe"
        
        ; Add uninstaller
        WriteUninstaller "$INSTDIR\\uninstall.exe"
        WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{APP_NAME}" \
                        "DisplayName" "{APP_NAME}"
        WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{APP_NAME}" \
                        "UninstallString" "$INSTDIR\\uninstall.exe"
    SectionEnd
    
    Section "Uninstall"
        ; Remove files
        RMDir /r "$INSTDIR"
        
        ; Remove shortcuts
        Delete "$SMPROGRAMS\\{APP_NAME}\\*.*"
        RMDir "$SMPROGRAMS\\{APP_NAME}"
        Delete "$DESKTOP\\{APP_NAME}.lnk"
        
        ; Remove registry keys
        DeleteRegKey HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{APP_NAME}"
    SectionEnd
    """
    
    with open(BUILD_DIR / "installer.nsi", "w") as f:
        f.write(nsis_script)
    
    # Build installer
    run_command(["makensis", str(BUILD_DIR / "installer.nsi")])
    print(f"Windows installer created at: {DIST_DIR / f'{APP_NAME.replace(" ", "")}-{VERSION}-Setup.exe'}")

def build_mac():
    """Build macOS application bundle and DMG."""
    print("Building macOS application bundle...")
    
    # Create app bundle
    run_command([
        "py2applet", "--make-setup", "main.py",
        f"--name={APP_NAME.replace(' ', '')}",
        f"--iconfile={BASE_DIR / 'resources' / 'icons' / 'maya.icns'}",
        "--packages=PyQt6",
        "--resources=resources"
    ])
    
    # Build the app
    run_command(["python", "setup.py", "py2app"])
    
    # Create DMG
    # Using triple quotes and .format() to avoid f-string issues with AppleScript braces
    dmg_script = """
    set appPath to "{app_path}"
    set dmgPath to "{dmg_path}"
    
    tell application "Finder"
        set dmgDir to POSIX file "{dist_dir}" as text
        set tempDir to (POSIX file "{build_dmg_dir}" as text)
        
        -- Create temp directory
        do shell script "mkdir -p " & quoted form of POSIX path of tempDir
        
        -- Copy app to temp dir
        do shell script "cp -R " & quoted form of POSIX path of appPath & " " & quoted form of POSIX path of tempDir
        
        -- Create DMG
        set volumeName to "{app_name} {version}"
        set diskImagePath to dmgPath
        set srcFolder to tempDir
        
        try
            set diskImage to "hdiutil create -volname " & quoted form of volumeName & \
                          " -srcfolder " & quoted form of POSIX path of srcFolder & \
                          " -ov " & quoted form of POSIX path of diskImagePath
            do shell script diskImage
            
            -- Set window position and size
            set windowPosition to {{100, 100}, {640, 520}}
            
            tell application "Finder"
                open diskImagePath as POSIX file
                set windowId to id of window 1
                set bounds of window id windowId to windowPosition
                close window id windowId saving no
            end tell
            
            return "DMG created successfully at: " & diskImagePath
        on error errMsg
            return "Error creating DMG: " & errMsg
        end try
    end tell
    """.format(
        app_path=str(DIST_DIR / f"{APP_NAME.replace(' ', '')}.app"),
        dmg_path=str(DIST_DIR / f"{APP_NAME.replace(' ', '')}-{VERSION}.dmg"),
        dist_dir=str(DIST_DIR),
        build_dmg_dir=str(BUILD_DIR / 'dmg'),
        app_name=APP_NAME,
        version=VERSION
    )
    
    with open(BUILD_DIR / "create_dmg.scpt", "w") as f:
        f.write(dmg_script)
    
    run_command(["osascript", str(BUILD_DIR / "create_dmg.scpt")])
    print(f"macOS DMG created at: {DIST_DIR / f'{APP_NAME.replace(" ", "")}-{VERSION}.dmg'}")

def build_linux():
    """Build Linux packages (DEB and RPM)."""
    print("Building Linux packages...")
    
    # Create directory structure
    app_name_lower = APP_NAME.lower().replace(" ", "-")
    debian_dir = BUILD_DIR / f"{app_name_lower}_{VERSION}"
    debian_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy files
    app_dir = debian_dir / f"usr/share/{app_name_lower}"
    app_dir.mkdir(parents=True, exist_ok=True)
    
    # Create desktop file
    desktop_file = f"""
    [Desktop Entry]
    Name={APP_NAME}
    Comment={DESCRIPTION}
    Exec=/usr/share/{app_name_lower}/maya
    Icon=/usr/share/{app_name_lower}/resources/icons/maya.png
    Terminal=false
    Type=Application
    Categories=Utility;Application;
    """
    
    (debian_dir / "usr/share/applications" / f"{app_name_lower}.desktop").parent.mkdir(parents=True, exist_ok=True)
    with open(debian_dir / "usr/share/applications" / f"{app_name_lower}.desktop", "w") as f:
        f.write(desktop_file)
    
    # Build DEB package
    print("Building DEB package...")
    run_command([
        "dpkg-deb", "--build", str(debian_dir),
        str(DIST_DIR / f"{app_name_lower}_{VERSION}_all.deb")
    ])
    
    # Build RPM package (requires rpmbuild)
    if shutil.which("rpmbuild"):
        print("Building RPM package...")
        rpm_dir = BUILD_DIR / "rpmbuild"
        rpm_dir.mkdir(parents=True, exist_ok=True)
        
        spec_file = f"""
        Name: {app_name_lower}
        Version: {VERSION}
        Release: 1
        Summary: {DESCRIPTION}
        License: MIT
        URL: https://github.com/yourusername/maya-ai
        
        %description
        {DESCRIPTION}
        
        %files
        /usr/
        
        %post
        desktop-file-install /usr/share/applications/{app_name_lower}.desktop
        update-desktop-database
        """
        
        with open(BUILD_DIR / f"{app_name_lower}.spec", "w") as f:
            f.write(spec_file)
        
        run_command(["rpmbuild", "-bb", "--buildroot", str(rpm_dir), str(BUILD_DIR / f"{app_name_lower}.spec")])
        
        # Move RPM to dist directory
        rpm_file = list((Path.home() / "rpmbuild/RPMS").glob(f"**/{app_name_lower}-{VERSION}-1.*.rpm"))[0]
        shutil.move(rpm_file, DIST_DIR / rpm_file.name)
    
    print(f"Linux packages created in: {DIST_DIR}")

def main():
    """Main build function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Build MAYA AI Chatbot installers")
    parser.add_argument("--clean", action="store_true", help="Clean build directories before building")
    parser.add_argument("--install-deps", action="store_true", help="Install build dependencies")
    parser.add_argument("--platform", choices=["all", "windows", "mac", "linux"], 
                       default={"Windows": "windows", "Darwin": "mac", "Linux": "linux"}.get(platform.system(), "all"),
                       help="Target platform to build for")
    
    args = parser.parse_args()
    
    if args.clean:
        clean_build()
    
    if args.install_deps:
        install_dependencies()
    
    # Create dist directory
    DIST_DIR.mkdir(exist_ok=True)
    
    # Build for the specified platform(s)
    target_platforms = []
    if args.platform == "all":
        target_platforms = ["windows", "mac", "linux"]
    else:
        target_platforms = [args.platform]
    
    for platform_name in target_platforms:
        try:
            if platform_name == "windows" and (IS_WINDOWS or args.platform != "all"):
                build_windows()
            elif platform_name == "mac" and (IS_MAC or args.platform != "all"):
                build_mac()
            elif platform_name == "linux" and (IS_LINUX or args.platform != "all"):
                build_linux()
        except Exception as e:
            print(f"Error building for {platform_name}: {e}")
            if args.platform != "all":
                raise

if __name__ == "__main__":
    main()
