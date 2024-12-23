from setuptools import setup

setup(name='async-parse-tools',
      version='0.2.4',
      description='Async Parse Tools',
      author='',
      author_email='',
      python_requires=">=3.10, <4",
      url='https://github.com/sleppyKid/async-parse-tools.git',
      packages=['async_parse_tools'],
      install_requires=[
          'aiohttp~=3.10.11',
          'aiofile~=3.8.1',
          'tqdm~=4.66.3',
          'asyncio-pool~=0.6.0',
          'playwright~=1.27.1'
      ],
      )
