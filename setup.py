from setuptools import setup

setup(
    name = "django-tojson",
    version = "0.3.0",
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

