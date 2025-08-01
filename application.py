"""
Application entry point for Elastic Beanstalk
This file is used by Elastic Beanstalk to start the FastAPI application
"""

from app import app

# This is the application object that Elastic Beanstalk expects
application = app

if __name__ == "__main__":
    application.run() 