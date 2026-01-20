from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="wine-store",
    version="1.0.0",
    author="Максим",
    author_email="maksim@example.com",
    description="Приложение для управления винной коллекцией с поддержкой экспорта в PDF и Excel",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/username/wine-store",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Office/Business",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "wine-store=main:main",
            "winestore=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.sql", "*.md", "*.txt", "*.toml", ".env.example"],
    },
    project_urls={
        "Bug Reports": "https://github.com/username/wine-store/issues",
        "Source": "https://github.com/username/wine-store",
        "Documentation": "https://github.com/username/wine-store/docs",
    },
)
