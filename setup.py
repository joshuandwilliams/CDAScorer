from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="CDAScorer",
    version='0.0.0.dev1',
    packages = ['CDAScorer', 'CDAScorer-data'],
    url="https://github.com/joshuandwilliams/CDAScorer",
    license='LICENSE.txt',
    author="Joshua Williams",
    author_email="<jowillia@nbi.ac.uk>",
    description='Cell Death Area Data Collection',
    long_description=long_description,
    long_description_content_type="text/markdown",
    scripts=['scripts/CDAScorer-test', 'scripts/CDAScorer-run'],
    include_package_data=True,
    package_data={"CDAScorer-data": ['lesion_score_key.jpg', 'test_cda_img.jpg']},
    install_requires=['opencv-python', 'pandas', 'natsort', 'importlib_resources', 'Pillow']
)
