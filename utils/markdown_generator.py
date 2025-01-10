import os
from pathlib import Path

class MarkdownGenerator:
    def __init__(self):
        self.ignored_dirs = {'.git', '__pycache__', 'node_modules', '.pythonlibs'}
        self.markdown_content = []
        self.BINARY_FILE_EXTENSIONS = {'.pyc', '.pyo', '.pyd', '.so', '.dll', '.exe', '.bin', '.jpg', '.jpeg', '.png', '.gif', '.pdf'}

    def generate_markdown(self, repo_path):
        """
        Generate markdown content from repository files
        """
        try:
            self.markdown_content = []

            # Add repository structure first
            self.markdown_content.append("# Repository Structure\n")
            self._generate_structure(repo_path)

            # Add separator
            self.markdown_content.append("\n# File Contents\n")

            # Process all files with their contents
            self._process_directory(repo_path)
            return '\n'.join(self.markdown_content)
        except Exception as e:
            raise Exception(f"Failed to generate markdown: {str(e)}")

    def _generate_structure(self, directory, level=0):
        """
        Generate repository structure in markdown format
        """
        try:
            items = sorted(Path(directory).iterdir())
            for item in items:
                if item.name in self.ignored_dirs:
                    continue

                indent = "  " * level
                relative_path = os.path.relpath(item, directory)

                if item.is_dir():
                    self.markdown_content.append(f"{indent}- {relative_path}/")
                    self._generate_structure(item, level + 1)
                else:
                    self.markdown_content.append(f"{indent}- {relative_path}")

        except Exception as e:
            self.markdown_content.append(f"*Error processing directory structure {directory}: {str(e)}*")

    def _is_binary_file(self, file_path):
        """
        Quick check if file is binary based on extension or content
        """
        if file_path.suffix.lower() in self.BINARY_FILE_EXTENSIONS:
            return True

        try:
            with open(file_path, 'rb') as f:
                chunk = f.read(1024)
                return b'\0' in chunk
        except:
            return True

    def _process_directory(self, directory, level=0):
        """
        Process directory and generate markdown content with file contents
        """
        try:
            items = sorted(Path(directory).iterdir())

            for item in items:
                if item.name in self.ignored_dirs:
                    continue

                relative_path = os.path.relpath(item, start=directory)

                if item.is_dir():
                    self._process_directory(item, level + 1)
                else:
                    # Add file header
                    self.markdown_content.append(f"\n## File: {relative_path}")
                    try:
                        self._add_file_content(item)
                    except Exception as e:
                        self.markdown_content.append(f"*Error reading file: {str(e)}*")

        except Exception as e:
            self.markdown_content.append(f"*Error processing directory {directory}: {str(e)}*")

    def _add_file_content(self, file_path):
        """
        Add file content to markdown with proper formatting
        """
        try:
            if self._is_binary_file(file_path):
                self.markdown_content.append("*Binary file - content not shown*\n")
                return

            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if content.strip():
                    self.markdown_content.append("```" + file_path.suffix.lstrip('.'))
                    self.markdown_content.append(content)
                    self.markdown_content.append("```\n")

        except UnicodeDecodeError:
            self.markdown_content.append("*Binary file - content not shown*\n")
        except Exception as e:
            raise Exception(f"Error reading file {file_path}: {str(e)}")