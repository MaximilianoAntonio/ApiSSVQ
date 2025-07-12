#!/usr/bin/env python
"""
Command-line utility for administrative tasks on Azure.
"""
import os
import sys

if __name__ == '__main__':
    """Run administrative tasks."""
    # Set Django settings module for Azure
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestor_vehiculos.settings_azure')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)
