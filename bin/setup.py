try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'URL Shortner',
    'author': 'Amin',
    'url': '',
    'download_url': 'Where to download it.',
    'author_email': 'aminkhorsandi@gmail.com',
    'version': '0.1',
    'install_requires': ['nose, webpy'],
    'packages': ['url_shortner'],
    'scripts': [],
    'name': 'url_shortner'
}

setup(**config)
