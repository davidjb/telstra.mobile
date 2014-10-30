from setuptools import setup, find_packages

version = '0.1'

long_description = (
    open('README.rst').read()
    + '\n' +
    'Contributors\n'
    '============\n'
    + '\n' +
    open('docs/CONTRIBUTORS.rst').read()
    + '\n' +
    open('docs/CHANGES.rst').read()
    + '\n')

setup(name='telstra.mobile',
      version=version,
      description="API for interacting with Telstra's mobile services via cellular modem",
      long_description=long_description,
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
          "Programming Language :: Python",
          "Development Status :: 1 - Planning",
          "Environment :: Console",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: MIT License",
          "Operating System :: OS Independent",
          "Topic :: Software Development :: Libraries :: Python Modules",
      ],
      keywords='Modem Serial pySerial GSM Telstra Cellular Modem',
      author='David Beitey',
      author_email='david' + chr(64) + 'davidjb.com',
      url='https://github.com/davidjb/telstra.mobile',
      license='MIT',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      namespace_packages=['telstra'],
      include_package_data=True,
      zip_safe=False,
      setup_requires=['setuptools-git'],
      install_requires=[
          'setuptools',
          'python-gsmmodem',
          'pyserial',
          'serialenum',
          'lazy',
          'requests',
          'envelopes',
          # -*- Extra requirements: -*-
      ],
      extras_require={
          'test': [],
          'doc': ['sphinx'],
      },
      entry_points="""
      # -*- Entry points: -*-
      [console_scripts]
      send-credit = telstra.mobile.scripts.send_credit:main
      """,
      )
