from distutils.core import setup


setup(
    name="stomp",
    description="STOMP 1.2 client library",
    author="Cochise Ruhulessin",
    author_email="cochise.ruhulessin@sousouindustries.com",
    url="https://github.com/sousouindustries/python-stomp",
    packages=['stomp'],
    package_dir={'stomp': 'src/stomp'}
)
