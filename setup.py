from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="cdascorer",
    version='0.0.0.dev8',
    packages = ['cdascorer', 'cdascorer-data'],
    url="https://github.com/joshuandwilliams/CDAScorer",
    license='LICENSE.txt',
    author="Joshua Williams",
    author_email="<jowillia@nbi.ac.uk>",
    description='Cell Death Area Data Collection',
    long_description=long_description,
    long_description_content_type="text/markdown",
    scripts=['scripts/cdascorer', 'scripts/cdascorer-test', 'scripts/cdascorer-windows.py', 'scripts/cdascorer-windows-test.py'],
    include_package_data=True,
    package_data={"cdascorer-data": ['lesion_score_key.jpg', 'test_cda_img.jpg']},
    install_requires=['pandas', 'natsort', 'importlib_resources', 'Pillow']
)
