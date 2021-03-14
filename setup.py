import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="irds_robust_anserini",
    version="0.0.0",
    author="Sean MacAvaney",
    author_email="sean@ir.cs.georgetown.com",
    description="extension for ir_datasets that loads document content for robust04 from a public anserini index",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/seanmacavaney/irds_robust_anserini",
    include_package_data = True,
    packages=setuptools.find_packages(include=['irds_robust_anserini']),
    install_requires=list(open('requirements.txt')),
    classifiers=[],
    python_requires='>=3.6'
)
