from setuptools import find_packages, setup

setup(
    name="log-analytics",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "boto3",
        "fastapi",
        "python-dotenv",
        "python-dateutil",
        "uvicorn"
    ],
    entry_points={
        "console_scripts": [
            "analyze=src.controllers.cli.analyze:main",
        ],
    },
)
