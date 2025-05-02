from setuptools import setup, find_packages

setup(
    name="apnea_trainer",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "fastapi==0.109.2",
        "uvicorn==0.27.1",
        "tomli==2.0.1",
        "jinja2==3.1.3",
        "python-multipart==0.0.9",
    ],
    python_requires=">=3.11",
) 