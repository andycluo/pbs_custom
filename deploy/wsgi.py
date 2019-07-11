"""
WSGI config for deploy project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/howto/deployment/wsgi/
"""

import os
import sys
import importlib

sys.path.append(os.path.abspath(os.path.dirname(__file__)))
sys.path.append('/opt/deploy/')
sys.path.append('/opt/deploy/deploy')
sys.path.append('/opt/deploy/publishs')
#importlib.reload(sys)

#sys.setdefaultencoding('utf-8')

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "deploy.settings")

application = get_wsgi_application()
