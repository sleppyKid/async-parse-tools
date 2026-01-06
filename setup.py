from setuptools import setup

setup(name='async-parse-tools',
      version='0.2.5',
      description='Async Parse Tools',
      author='',
      author_email='',
      python_requires=">=3.10, <4",
      url='https://github.com/sleppyKid/async-parse-tools.git',
      packages=['async_parse_tools'],
      install_requires=[
          'aiohttp~=3.13.3',
          'aiofile~=3.9.0',
          'tqdm~=4.67.1',
          'asyncio-pool~=0.6.0',
          'playwright~=1.57.0'
      ],
      )
