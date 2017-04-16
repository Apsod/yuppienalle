from setuptools import setup, find_packages

setup(name='yuppie',
      version='0.0.1',
      description='server for yuppienalle',
      requires=['numpy', 'autobahn'],
      packages=find_packages(),
      entry_points={
            'console_scripts': [
                  'run-yuppie = yuppie.server:run'
            ]
          },
      )
