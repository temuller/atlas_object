import setuptools

with open("README.md", "r") as readme_file:
    long_description = readme_file.read()

with open("requirements.txt", "r") as requirements_file:
    requirements = requirements_file.read().splitlines()

with open("atlas_object/_version.py", "r") as version_file:
    for line in version_file:
        if "__version__" in line:
            __version__ = line.split()[-1].replace('"', "")

setuptools.setup(
    name="ATLAS Object",
    version=__version__,
    author="Tomás Enrique Müller-Bravo",
    author_email="t.e.muller-bravo@ice.csic.es",
    license="MIT",
    description="For clening ATLAS light curves",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/temuller/atlas_object",
    packages=setuptools.find_packages(),
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=requirements,
    #package_data={},
    include_package_data=True,
)
