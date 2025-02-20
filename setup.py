from setuptools import setup, find_packages

setup(
    name="wr-cl",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "python-docx>=0.8.11",
    ],
    entry_points={
        "console_scripts": [
            "wr-cl=src.cli:main",
        ],
    },
    python_requires=">=3.7",
    author="lanseria",
    description="Word replacer command line tool",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)