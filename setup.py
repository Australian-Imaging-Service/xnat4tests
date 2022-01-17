import versioneer
from setuptools import setup, find_packages


setup(
    name='xnat4tests',
    version=versioneer.get_version(),
    author='Thomas G. Close',
    author_email='tom.g.close@gmail.com',
    packages=find_packages(),
    url='https://github.com/australian-imaging-service/xnat4tests',
    license='CC0',
    description=('Creates basic XNAT instance for API tests'),
    long_description=open('README.rst').read(),
    install_requires=[
        'docker>=5.0.2',
        'xnat>=0.3.17',
        'requests>=2.10.0'],
    extras_require={
        'test': [
            'pytest>=5.4.3']},
    include_package_data=True,
    cmdclass=versioneer.get_cmdclass(),
    classifiers=(
        ["Development Status :: 4 - Beta",
         "Intended Audience :: Healthcare Industry",
         "Intended Audience :: Science/Research",
         "License :: OSI Approved :: Apache Software License",
         "Natural Language :: English",
         "Topic :: Scientific/Engineering :: Bio-Informatics",
         "Topic :: Scientific/Engineering :: Medical Science Apps."]
        + ["Programming Language :: Python :: " + str(v)
           for v in ('3.5', '3.6', '3.7', '3.8', '3.9')]),
    keywords='repository analysis neuroimaging workflows pipelines')
