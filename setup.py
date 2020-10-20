import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="dancing-art", # Replace with your own username
    version="0.0.1",
    author="Daniel Wardzinski",
    author_email="daniel.ward07@gmail.com",
    description="",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    py_modules=['dancing_art'],
    install_requires=[
        'numpy',
        'pandas',
        'matplotlib==3.0.3',
        'PySimpleGUI',
        'Pillow',
        'opencv-python',
        'moviepy',
        'librosa',
        'tqdm'
    ],
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'dancing-art = dancing_art.__main__:main',
        ],
    },
)