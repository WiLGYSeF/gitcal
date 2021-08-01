import setuptools

with open('README.md', 'r', encoding='utf-8') as file:
    long_description = file.read()

setuptools.setup(
    name='gitcal',
    version='0.0.2',
    author='wilgysef',
    author_email='wilgysef@gmail.com',
    description='Visualize when git commits were made in a repository in a calendar-like format.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/WiLGYSeF/gitcal',
    project_urls={
        'Bug Tracker': 'https://github.com/WiLGYSeF/gitcal/issues',
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    package_dir={'': 'src'},
    packages=setuptools.find_packages(where='src'),
    python_requires='>=3.6',
    entry_points={
        'console_scripts': ['gitcal=gitcal.__main__:main']
    }
)
