from setuptools import setup, find_packages

setup(
    name="Security Alarm Setup",
    version="0.1",
    packages=find_packages(),

    # include data files
    package_data={
        "HeadlessSetup" : ["data/*.yml"],
    },

    # setup command line access
    entry_points={
        'console_scripts' : [
            'Run-Alarm-Setup = HeadlessSetup.AutomatedSetup:main',
        ]
    }
)

