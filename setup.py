from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "SecurityLog Guardian - Lightweight, smart, open-source log analyzer for web servers"

setup(
    name="securitylog-guardian",
    version="1.0.0",
    author="shadow1x0",
    author_email="your-email@example.com",
    description="Lightweight, smart, open-source log analyzer for web servers",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/shadow1x0/securitylog-guardian",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Security",
        "Topic :: System :: Logging",
        "Topic :: System :: Monitoring",
    ],
    python_requires=">=3.8",
    install_requires=[
        "PyYAML>=6.0",
        "requests>=2.28.0",
    ],
    extras_require={
        "dashboard": [
            "Flask>=2.3.0",
        ],
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
        ],
        "performance": [
            "ujson>=5.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "securitylog-guardian=guardian.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "guardian": ["../assets/*.json", "../assets/*.yaml"],
    },
    keywords="security, logging, monitoring, web-server, nginx, apache, threat-detection",
    project_urls={
        "Bug Reports": "https://github.com/shadow1x0/securitylog-guardian/issues",
        "Source": "https://github.com/shadow1x0/securitylog-guardian",
        "Documentation": "https://github.com/shadow1x0/securitylog-guardian#readme",
    },
) 