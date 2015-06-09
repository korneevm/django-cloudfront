from setuptools import setup

setup(
    name='django_cloudfront',
    version='0.2',
    description='Amazon CloudFront private content signing for Django',
    url='http://github.com/korneevm/django_cloudfront',
    author='tzangms,korneevm',
    author_email='tzangms@gmail.com, korneevm@gmail.com',
    keywords='django cloudfront',
    classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Framework :: Django",
        "Environment :: Web Environment",
    ],
    license='MIT',
    packages=['cloudfront'],
    install_requires=[
        'pycrypto==2.6',
    ],
    zip_safe=False
)
