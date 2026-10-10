from setuptools import setup, find_packages

setup(
    name="apex-hypergate",
    version="1.0.0",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "hypergate=apex_hypergate.cli:main",
        ],
    },
)
