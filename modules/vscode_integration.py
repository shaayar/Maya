"""
VS Code Integration for MAYA AI Chatbot.
Handles communication and interaction with VS Code.
"""

import os
import subprocess
import json
from pathlib import Path
from typing import Optional, Dict, List, Union, Any
import logging

logger = logging.getLogger(__name__)

class VSCodeIntegration:
    """Handles integration with Visual Studio Code."""
    
    def __init__(self):
        """Initialize the VS Code integration."""
        self.vscode_path = self._find_vscode_executable()
        self.is_available = self.vscode_path is not None
        
        if not self.is_available:
            logger.warning("VS Code not found. Some features will be disabled.")
    
    def _find_vscode_executable(self) -> Optional[str]:
        """Find the VS Code executable path."""
        # Common VS Code installation paths
        paths = [
            "code",  # Linux/macOS (in PATH)
            "/usr/bin/code",  # Linux
            "/usr/local/bin/code",  # macOS (Homebrew)
            "/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code",  # macOS
            os.path.expandvars(r"%LOCALAPPDATA%\\Programs\\Microsoft VS Code\\bin\\code.cmd"),  # Windows User
            os.path.expandvars(r"%PROGRAMFILES%\\Microsoft VS Code\\bin\\code.cmd"),  # Windows System
        ]
        
        for path in paths:
            try:
                if os.path.exists(path) or (os.path.isfile(path) and os.access(path, os.X_OK)):
                    return path
                # Check if 'code' is in PATH
                if path == "code" and subprocess.run(["which", "code"], capture_output=True).returncode == 0:
                    return "code"
            except Exception:
                continue
        
        return None
    
    def open_file(self, file_path: Union[str, Path], line: Optional[int] = None, column: Optional[int] = None) -> bool:
        """
        Open a file in VS Code.
        
        Args:
            file_path: Path to the file to open
            line: Line number to navigate to (1-based)
            column: Column number to navigate to (1-based)
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.is_available:
            return False
            
        try:
            file_path = str(Path(file_path).resolve())
            args = [self.vscode_path, "--new-window", file_path]
            
            if line is not None:
                args.extend(["--goto", f"{file_path}:{line}{f':{column}' if column else ''}"])
            
            subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return True
        except Exception as e:
            logger.error(f"Error opening file in VS Code: {e}")
            return False
    
    def open_folder(self, folder_path: Union[str, Path]) -> bool:
        """
        Open a folder in VS Code.
        
        Args:
            folder_path: Path to the folder to open
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.is_available:
            return False
            
        try:
            folder_path = str(Path(folder_path).resolve())
            subprocess.Popen([self.vscode_path, "--new-window", folder_path], 
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return True
        except Exception as e:
            logger.error(f"Error opening folder in VS Code: {e}")
            return False
    
    def execute_command(self, command_id: str, args: Optional[Dict[str, Any]] = None) -> bool:
        """
        Execute a VS Code command.
        
        Args:
            command_id: The VS Code command ID
            args: Optional arguments for the command
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.is_available:
            return False
            
        try:
            cmd = [self.vscode_path, "--command", command_id]
            if args:
                cmd.extend(["--args-json", json.dumps(args)])
            
            subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return True
        except Exception as e:
            logger.error(f"Error executing VS Code command: {e}")
            return False
    
    def install_extension(self, extension_id: str) -> bool:
        """
        Install a VS Code extension.
        
        Args:
            extension_id: The extension ID (e.g., 'ms-python.python')
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.is_available:
            return False
            
        try:
            result = subprocess.run(
                [self.vscode_path, "--install-extension", extension_id],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                logger.error(f"Failed to install extension {extension_id}: {result.stderr}")
                return False
                
            logger.info(f"Successfully installed extension: {extension_id}")
            return True
        except Exception as e:
            logger.error(f"Error installing VS Code extension: {e}")
            return False
    
    def list_extensions(self) -> List[Dict[str, str]]:
        """
        List installed VS Code extensions.
        
        Returns:
            List of dictionaries containing extension information
        """
        if not self.is_available:
            return []
            
        try:
            result = subprocess.run(
                [self.vscode_path, "--list-extensions", "--show-versions"],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                logger.error(f"Failed to list extensions: {result.stderr}")
                return []
                
            extensions = []
            for line in result.stdout.splitlines():
                if '@' in line:
                    name, version = line.split('@', 1)
                    extensions.append({"name": name, "version": version})
                else:
                    extensions.append({"name": line, "version": "unknown"})
                    
            return extensions
        except Exception as e:
            logger.error(f"Error listing VS Code extensions: {e}")
            return []
    
    def is_vscode_running(self) -> bool:
        """
        Check if VS Code is currently running.
        
        Returns:
            bool: True if VS Code is running, False otherwise
        """
        try:
            if os.name == 'nt':  # Windows
                import psutil
                return any('code' in p.name().lower() for p in psutil.process_iter(['name']))
            else:  # Linux/macOS
                result = subprocess.run(['pgrep', '-f', 'code'], capture_output=True)
                return result.returncode == 0
        except Exception as e:
            logger.error(f"Error checking if VS Code is running: {e}")
            return False
