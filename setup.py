from setuptools import setup, find_packages
import os

# Read the contents of your README file
with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

# Get version from a version file or other source
version = '1.0.0'

# Define dependencies
install_requires = [
    'PyQt6>=6.0.0',
    'pyttsx3>=2.90',
    'SpeechRecognition>=3.8.1',
    'pytesseract>=0.3.8',
    'opencv-python>=4.5.3',
    'numpy>=1.21.0',
    'Pillow>=8.3.1',
    'pywin32>=300;platform_system=="Windows"',  # Windows specific
    'pyobjc>=7.3;platform_system=="Darwin"',   # macOS specific
    'pycairo>=1.20.0;platform_system=="Linux"', # Linux specific
]

# Data files to include
package_data = {
    '': ['*.json', '*.md', '*.txt'],
    'modules': ['*.py'],
}

# Entry points
entry_points = {
    'console_scripts': [
        'maya-ai=main:main',
    ],
}

setup(
    name="maya-ai",
    version=version,
    author="MAYA Development Team",
    author_email="support@maya-ai.com",
    description="MAYA AI Chatbot - A powerful AI assistant with voice and screen interaction capabilities",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/maya-ai",
    packages=find_packages(),
    package_data=package_data,
    include_package_data=True,
    install_requires=install_requires,
    entry_points=entry_points,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Desktop Environment",
        "Topic :: Utilities",
    ],
    python_requires='>=3.8',
)
