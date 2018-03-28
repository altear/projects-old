from setuptools import setup, find_packages
setup(
    name="GetTestImages",
    author="Andre Telfer",
    author_email="telfer006@gmail.com",
    description="Pull test images from imagenet to gauge performance of security net",
    version="0.4",
    packages=find_packages(),
    install_requires=[
        'requests>=2.0.0'
    ],
    entry_points = {
        'console_scripts' : ['get-test-images=get_test_images.get_test_images:main']
    }
)