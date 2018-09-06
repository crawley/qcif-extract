from setuptools import setup

setup(name='qcif-extract',
      version='0.1',
      description='The QCIF NeCTAR extraction tool',
      url='http://github.com/crawley/qcif-extract',
      author='Stephen Crawley',
      author_email='s.crawley@uq.edu.au',
      license='MIT',
      packages=['extract'],
      install_requires=[
          'os-client-config',
          'python-novaclient',
          'python-neutronclient',
          'python-keystoneclient',
          'nectarallocationclient',
          'mysql-connector-python'
      ],
      zip_safe=False)
