# coding: utf-8
from setuptools import setup

setup(
    name="PlaceBot",
    version="0.1.0",
    packages=["place_bot"],
    install_requires=[
        "requests",
        "websocket-client",
        "beautifulsoup4",
        "numpy",
        "Pillow",
    ],
)
