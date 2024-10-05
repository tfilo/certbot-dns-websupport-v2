import os
import sys

from setuptools import find_packages
from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

version = "1.0.1"

# acme/certbot version.
install_requires = [
    "certbot>=2.11.0",
    "setuptools",
    "requests",
]

docs_extras = [
    "Sphinx>=1.0",  # autodoc_member_order = 'bysource', autodoc_default_flags
    "sphinx_rtd_theme",
]

setup(
    name="certbot-dns-websupport-v2",
    version=version,
    description="Websupport DNS Authenticator plugin for Certbot",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tfilo/certbot-dns-websupport-v2",
    author="Tomáš Filo",
    author_email="tfilosk@gmail.com",
    license="Apache",
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Plugins",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Security",
        "Topic :: System :: Installation/Setup",
        "Topic :: System :: Networking",
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities",
    ],
    packages=find_packages(),
    include_package_data=True,
    install_requires=install_requires,
    extras_require={
        "docs": docs_extras,
    },
    entry_points={
        "certbot.plugins": [
            "dns-websupport-v2 = certbot_dns_websupport_v2.dns_websupport_v2:Authenticator",
        ],
    },
)
