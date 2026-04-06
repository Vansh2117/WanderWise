from setuptools import setup, find_packages

setup(
    name="WanderWise",
    version="0.1.0",
    description="AI-powered trip planning app",
    author="Vansh Sharma",
    packages=find_packages(),
    install_requires=[
        "fastapi[standard]",
        "sqlalchemy",
        "httpx",
        "python-dotenv",
        "scikit-learn",
        "matplotlib",
        "seaborn",
        "dill",
        "uvicorn",
        "passlib[bcrypt]", 
        "pydantic",
        "pydantic[email]",
    ],
)
