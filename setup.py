from setuptools import setup, find_packages
import os

version = '0.0.1'

setup(
    name='arv.factory',
    version=version,
    description="Test fixtures replacement for python.",
    long_description=open("README.rst").read(),
    # Get more strings from
    # http://pypi.python.org/pypi?:action=list_classifiers
    classifiers=[
        "Programming Language :: Python",
    ],
      keywords='',
    author='Alexis Roda',
    author_email='alexis.roda.villalonga@gmail.com',
    url='https://github.com/patxoca/arv.factory',
    license='GPL',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['arv'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        # -*- Extra requirements: -*-
        "six",
    ],
      entry_points="""
      # -*- Entry points: -*-
      """,
)
