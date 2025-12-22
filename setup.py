from setuptools import setup, find_packages

# To handle encoding issues, especially on Windows
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="react2shell",
    version="1.0.0",
    author="@BlackTechX011",
    author_email="",
    description="Advanced CVE-2025-55182 Exploitation Framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/BlackTechX011/React2Shell",
    packages=find_packages(),
    install_requires=[
        "requests>=2.28.0",
        "rich>=13.0.0",
        "tqdm>=4.64.0",
    ],
    entry_points={
        "console_scripts": [
            "react2shell=react2shell.__main__:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Security",
    ],
    python_requires=">=3.9",
)
