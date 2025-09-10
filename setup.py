from setuptools import setup, find_packages

setup(
    name="ytlite",
    version="0.2.0",
    packages=find_packages(),
    install_requires=[
        'pyyaml>=6.0.1',
        'markdown>=3.5.1',
        'python-frontmatter>=1.0.1',
        'edge-tts>=6.1.9',
        'moviepy>=1.0.3',
        'pillow>=10.2.0',
        'google-api-python-client>=2.108.0',
        'google-auth-oauthlib>=1.1.0',
        'click>=8.1.7',
        'rich>=13.7.0',
        'requests>=2.31.0',
        'schedule>=1.2.0',
        'python-dotenv>=1.0.0',
        'pytest>=7.4.0',
        'watchdog>=3.0.0',
        'openai-whisper>=20231117',
        'numpy>=1.24.0',
    ],
    author="Tom Sapletta",
    author_email="tom@sapletta.com",
    description="A minimalist YouTube content automation pipeline",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/tom-sapletta-com/ytlite",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.9',
    entry_points={
        'console_scripts': [
            'ytlite=src.ytlite:main',
        ],
    },
)
