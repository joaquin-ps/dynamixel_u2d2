#!/usr/bin/env python3
"""
Setup script for dynamixel_u2d2 package
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "Dynamixel U2D2 Interface Package"

# Read requirements
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return [
        "dynamixel-sdk>=3.7.0",
        "numpy>=1.19.0",
    ]

setup(
    name="dynamixel-u2d2",
    version="1.0.0",
    author="Finger Aloha Team",
    author_email="your-email@example.com",
    description="A clean, high-level interface for controlling Dynamixel motors through the U2D2 communication bridge",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/dynamixel-u2d2",  # Update with your actual repo
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.7",
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": [
            "dynamixel-scan=helpers.scan_dynamixel:main",
            "dynamixel-change-baud=helpers.change_baud:main",
            "dynamixel-change-id=helpers.change_id:main",
            "dynamixel-port=helpers.u2d2_port_timer:main",
        ],
    },
    include_package_data=True,
    package_data={
        "dynamixel_u2d2": [
            "*.sh",
            "examples/*.py",
            "helpers/*.py",
        ],
    },
    keywords="dynamixel u2d2 robotics motor control bulk operations",
    # project_urls={
    #     "Bug Reports": "https://github.com/your-username/dynamixel-u2d2/issues",
    #     "Source": "https://github.com/your-username/dynamixel-u2d2",
    #     "Documentation": "https://github.com/your-username/dynamixel-u2d2#readme",
    # },
)
