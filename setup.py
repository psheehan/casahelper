import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="casarecipes", 
    version="0.0.1",
    author="Patrick Sheehan",
    author_email="psheehan287@gmail.com",
    description="Recipes for data reduction with CASA.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/psheehan/casarecipes",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GPL3 License",
        "Operating System :: OS Independent",
    ],
    install_requires=['numpy'],
    python_requires='==3.6',
)
