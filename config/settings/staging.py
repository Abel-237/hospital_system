"""
Staging settings for Hospital Management System.
"""
from .prod import *

DEBUG = False
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['staging.hospital-cmr.local'])
