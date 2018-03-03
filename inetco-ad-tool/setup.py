from setuptools import setup, find_packages

setup(
    name="ad-toolkit",
    version="0.0.1",
    packages=find_packages(),

    # dependencies
    install_requires=[

    ],
    # scripts
    entry_points={
        'console_scripts' : [
            'ad-test1 = adtk.tests:test1',
            'ad-test2 = adtk.tests:test2',
            'gradle_to_maven = adtk.utils:main'
        ]
    },
)