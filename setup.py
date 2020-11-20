import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='teacher-helper',
    version='0.0.1',
    author='Jack DeVries',
    author_email='jdevries3133@gmail.com',
    description='Teacher task automation',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/jdevries3133/teacher-helper',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operateing System :: OS Independent',
    ],
    python_requires='>=3.8'
)
