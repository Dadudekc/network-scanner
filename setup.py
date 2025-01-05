from setuptools import setup, find_packages

setup(
    name="network_scanner",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A powerful network scanner and vulnerability assessment tool.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/network-scanner",
    packages=find_packages(),
    install_requires=[
        "requests",
        "packaging",
        "pandas",
        "numpy",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Security",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "network-scanner=network_scanner.__main__:main",  # Adjust based on your main entry point
        ],
    },
)
