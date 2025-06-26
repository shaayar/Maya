import os
import json
import fnmatch
from datetime import datetime
from typing import Optional, Dict, Any, List, Tuple, Set, Generator, Union
from pathlib import Path

class FileManager:
    """Handles all file operations for the application."""
    
    @staticmethod
    def create_file(file_path: str, content: str = "") -> bool:
        """Create a new file with optional content."""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"Error creating file {file_path}: {e}")
            return False
    
    @staticmethod
    def read_file(file_path: str) -> Optional[str]:
        """Read content from a file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            return None
    
    @staticmethod
    def append_to_file(file_path: str, content: str) -> bool:
        """Append content to an existing file."""
        try:
            with open(file_path, 'a', encoding='utf-8') as f:
                f.write(content + "\n")
            return True
        except Exception as e:
            print(f"Error appending to file {file_path}: {e}")
            return False
    
    @staticmethod
    def file_exists(file_path: str) -> bool:
        """Check if a file exists."""
        return os.path.exists(file_path)
    
    @staticmethod
    def find_files(
        root_dir: str,
        pattern: str = '*',
        content_search: Optional[str] = None,
        file_types: Optional[List[str]] = None,
        max_depth: int = 10
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Search for files matching the given criteria.
        
        Args:
            root_dir: Directory to search in
            pattern: Filename pattern (supports wildcards)
            content_search: Optional text to search within files
            file_types: List of file extensions to include (e.g., ['.py', '.txt'])
            max_depth: Maximum depth to search
            
        Yields:
            Dict with file information for each matching file
        """
        if file_types:
            file_types = {ext.lower() for ext in file_types}
            
        for root, dirs, files in os.walk(root_dir):
            # Calculate current depth
            depth = root[len(root_dir) + len(os.path.sep):].count(os.path.sep)
            if depth > max_depth:
                continue
                
            for filename in files:
                # Skip hidden files
                if filename.startswith('.'):
                    continue
                    
                # Check file extension
                if file_types and not any(filename.lower().endswith(ext) for ext in file_types):
                    continue
                    
                # Check filename pattern
                if not fnmatch.fnmatch(filename.lower(), pattern.lower()):
                    continue
                    
                file_path = os.path.join(root, filename)
                
                # Skip if content search is required but file is binary
                if content_search and FileManager.is_binary(file_path):
                    continue
                    
                # Check file content if needed
                if content_search:
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            if content_search.lower() not in content.lower():
                                continue
                    except (IOError, UnicodeDecodeError):
                        continue
                
                # Get file info
                file_info = FileManager.get_file_info(file_path)
                if file_info:
                    yield file_info
    
    @staticmethod
    def is_binary(file_path: str) -> bool:
        """Check if a file is binary."""
        try:
            with open(file_path, 'rb') as f:
                chunk = f.read(1024)
                return b'\0' in chunk
        except (IOError, OSError):
            return False
    
    @staticmethod
    def find_related_files(file_path: str, project_root: str) -> List[Dict[str, Any]]:
        """
        Find files that are related to the given file.
        
        For Python files, this looks for:
        - Files in the same directory
        - Files in the same package
        - Files with similar names (e.g., test_*.py for module.py)
        - Imported modules
        """
        if not os.path.isfile(file_path):
            return []
            
        file_dir = os.path.dirname(file_path)
        file_name = os.path.basename(file_path)
        file_base, file_ext = os.path.splitext(file_name)
        related = set()
        
        # Add files in the same directory
        for f in os.listdir(file_dir):
            if f != file_name:
                related.add(os.path.join(file_dir, f))
        
        # For Python files, look for related files
        if file_ext == '.py':
            # Look for test files
            test_file = os.path.join(file_dir, f'test_{file_name}')
            if os.path.isfile(test_file):
                related.add(test_file)
                
            # Look for files with similar names
            for f in os.listdir(file_dir):
                if f.startswith(file_base) and f != file_name:
                    related.add(os.path.join(file_dir, f))
        
        # Get file info for all related files
        return [FileManager.get_file_info(f) for f in related if os.path.isfile(f)]
    
    @staticmethod
    def create_code_file(
        file_path: str,
        file_type: str = 'python',
        template: Optional[str] = None,
        **template_vars
    ) -> bool:
        """
        Create a new code file with optional template.
        
        Args:
            file_path: Path where the file should be created
            file_type: Type of code file ('python', 'javascript', 'html', etc.)
            template: Optional template name to use
            **template_vars: Variables to use in the template
            
        Returns:
            bool: True if file was created successfully
        """
        if os.path.exists(file_path):
            return False
            
        # Default templates
        templates = {
            'python': {
                'default': (
                    '#!/usr/bin/env python3\n'
                    '# -*- coding: utf-8 -*-\n\n'
                    'def main():\n'
                    '    pass\n\n'
                    'if __name__ == "__main__":\n'
                    '    main()\n'
                ),
                'class': (
                    '#!/usr/bin/env python3\n'
                    '# -*- coding: utf-8 -*-\n\n'
                    'class {class_name}:\n'
                    '    """{docstring}"""\n\n'
                    '    def __init__(self):\n'
                    '        pass\n'
                )
            },
            'javascript': '// {filename}\n\n// Your code here\n',
            'html': (
                '<!DOCTYPE html>\n'
                '<html>\n'
                '<head>\n'
                '    <meta charset="UTF-8">\n'
                '    <title>{title}</title>\n'
                '</head>\n'
                '<body>\n'
                '    <!-- Your content here -->\n'
                '</body>\n'
                '</html>\n'
            )
        }
        
        # Get template content
        content = ''
        if template and file_type in templates and template in templates[file_type]:
            content = templates[file_type][template].format(
                filename=os.path.basename(file_path),
                class_name=template_vars.get('class_name', 'MyClass'),
                docstring=template_vars.get('docstring', 'Class docstring'),
                title=template_vars.get('title', 'New Page')
            )
        elif file_type in templates and isinstance(templates[file_type], str):
            content = templates[file_type].format(
                filename=os.path.basename(file_path),
                **template_vars
            )
        
        # Create parent directories if they don't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Write the file
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            # Make executable if it's a script
            if file_type in ['python', 'bash']:
                os.chmod(file_path, 0o755)
            return True
        except (IOError, OSError) as e:
            print(f"Error creating file {file_path}: {e}")
            return False
    
    @staticmethod
    def get_file_info(file_path: str) -> Optional[Dict[str, Any]]:
        """Get information about a file."""
        try:
            stat_info = os.stat(file_path)
            return {
                'size': stat_info.st_size,
                'created': datetime.fromtimestamp(stat_info.st_ctime).strftime('%Y-%m-%d %H:%M:%S'),
                'modified': datetime.fromtimestamp(stat_info.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                'is_file': os.path.isfile(file_path),
                'is_dir': os.path.isdir(file_path)
            }
        except Exception as e:
            print(f"Error getting file info for {file_path}: {e}")
            return None
