from setuptools import setup
import tojson

setup(
    name = "django-tojson",
    version = tojson.__version__,
    description = open("README", 'r').read(),
    url = "https://github.com/davidek/django-tojson",
    author="Davide Kirchner, Roberto Bampi",
    author_email="",
    packages = [
        "tojson"
    ],
    classifiers = [
        'Programming Language :: Python',
        'License :: OSI Approved :: GPL License',
        'Operating System :: OS Indipendent',
        'Framework :: Django',
    ]
)

