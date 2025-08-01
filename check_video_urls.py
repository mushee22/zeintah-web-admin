#!/usr/bin/env python3
"""
Script to check existing video URLs in SubChapters
"""

import os
import sys
import django
from django.conf import settings

# Add the project directory to Python path
sys.path.append('/Users/admin/Documents/zientah-app-admin')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'zeintah.settings')
django.setup()

from web.models import SubChapters

def check_video_urls():
    """Check existing video URLs in SubChapters"""
    print("=== Checking SubChapters Video URLs ===")
    
    subchapters = SubChapters.objects.all()
    print(f"Total SubChapters: {subchapters.count()}")
    
    for subchapter in subchapters:
        print(f"ID: {subchapter.id}, Title: {subchapter.title}")
        print(f"  Video: {subchapter.video}")
        print(f"  Video type: {type(subchapter.video)}")
        print("---")

if __name__ == "__main__":
    check_video_urls() 