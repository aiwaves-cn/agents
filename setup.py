import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ai-agents", 
    version="0.0.1",
    author="AIWaves",
    author_email="contact@aiwaves.cn",
    description="An Open-source Framework for Autonomous Language Agents",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/aiwaves-cn/agents",
    # packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages = ['agents'],
    python_requires='>=3.6',
    license='Apache License 2.0',
    install_requires=[
        'beautifulsoup4',
        'fastapi',
        'google_api_python_client',
        'google_auth_oauthlib',
        'gradio==3.39.0',
        'langchain',
        'numpy',
        'openai',
        'pandas',
        'Pillow',
        'protobuf',
        'psutil',
        'PyYAML',
        'Requests',
        'selenium',
        'sentence_transformers',
        'setuptools',
        'text2vec',
        'torch',
        'tqdm',
        'uvicorn'
    ]
)