"""
Application Framework Module
Version: 1.0.0
"""
from flask import Flask

try:
    """
    If the decorators folder is present
    """
    from application.decorators import LambdaDecorator

    class Application(Flask, LambdaDecorator):
        pass
except Exception as err:
    class Application(Flask):
        pass
