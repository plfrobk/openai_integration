from setuptools import find_packages
from setuptools import setup

setup(
    name='OpenAI_Integration',
    version='1.0',
    license='GNU General Public License',
    description='YOUR_DESCRIPTION',
    author='YOUR_INITIALS',
    author_email='YOUR_EMAIL@DOMAIN.COM',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        # complete classifier list: http://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Operating System :: Unix',
        'Operating System :: POSIX',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.11',
    ],
    keywords=[
        # eg: 'keyword1', 'keyword2', 'keyword3',
    ],
    python_requires='>=3.11',
    install_requires=[
        # eg: 'aspectlib==1.1.1', 'six>=1.7',
    ],
    extras_require={
        # eg:
        #   'rst': ['docutils>=0.11'],
        #   ':python_version=="2.6"': ['argparse'],
    },
    setup_requires=[
        # 'pytest-runner',
    ],
    entry_points={
        #'console_scripts': [
        #    'api = api.api:main',
        #]
    }
)