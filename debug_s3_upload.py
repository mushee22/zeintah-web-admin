#!/usr/bin/env python3
"""
Debug script to test S3 upload functionality
Run this script to check S3 configuration and test upload
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

def test_s3_configuration():
    """Test S3 configuration"""
    print("=== S3 Configuration Test ===")
    
    # Check if we're in production mode
    print(f"DEBUG mode: {settings.DEBUG}")
    
    # Check AWS credentials
    aws_access_key = getattr(settings, 'AWS_ACCESS_KEY_ID', None)
    aws_secret_key = getattr(settings, 'AWS_SECRET_ACCESS_KEY', None)
    aws_bucket = getattr(settings, 'AWS_STORAGE_BUCKET_NAME', None)
    aws_region = getattr(settings, 'AWS_S3_REGION_NAME', None)
    
    print(f"AWS_ACCESS_KEY_ID: {'✓ Set' if aws_access_key else '✗ Not set'}")
    print(f"AWS_SECRET_ACCESS_KEY: {'✓ Set' if aws_secret_key else '✗ Not set'}")
    print(f"AWS_STORAGE_BUCKET_NAME: {'✓ Set' if aws_bucket else '✗ Not set'}")
    print(f"AWS_S3_REGION_NAME: {'✓ Set' if aws_region else '✗ Not set'}")
    
    if not all([aws_access_key, aws_secret_key, aws_bucket, aws_region]):
        print("\n❌ S3 configuration is incomplete!")
        return False
    
    print("\n✅ S3 configuration looks good!")
    return True

def test_s3_client():
    """Test S3 client creation"""
    print("\n=== S3 Client Test ===")
    
    try:
        import boto3
        from botocore.exceptions import ClientError
        
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME
        )
        
        # Test bucket access
        response = s3_client.head_bucket(Bucket=settings.AWS_STORAGE_BUCKET_NAME)
        print("✅ S3 client created successfully")
        print("✅ Bucket access verified")
        return True
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == '404':
            print("❌ Bucket not found")
        elif error_code == '403':
            print("❌ Access denied to bucket")
        else:
            print(f"❌ S3 client error: {error_code}")
        return False
    except Exception as e:
        print(f"❌ S3 client creation failed: {str(e)}")
        return False

def test_presigned_url():
    """Test presigned URL generation"""
    print("\n=== Presigned URL Test ===")
    
    try:
        import boto3
        import uuid
        
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME
        )
        
        # Generate test presigned URL
        test_filename = f"test/{uuid.uuid4()}.mp4"
        presigned_url = s3_client.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                'Key': test_filename,
                'ContentType': 'video/mp4'
            },
            ExpiresIn=3600
        )
        
        print("✅ Presigned URL generated successfully")
        print(f"URL: {presigned_url[:100]}...")
        return True
        
    except Exception as e:
        print(f"❌ Presigned URL generation failed: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("S3 Upload Debug Script")
    print("=" * 50)
    
    # Test 1: Configuration
    config_ok = test_s3_configuration()
    
    if not config_ok:
        print("\n❌ Configuration test failed. Please check your S3 settings.")
        return
    
    # Test 2: S3 Client
    client_ok = test_s3_client()
    
    if not client_ok:
        print("\n❌ S3 client test failed. Please check your AWS credentials and bucket permissions.")
        return
    
    # Test 3: Presigned URL
    url_ok = test_presigned_url()
    
    if not url_ok:
        print("\n❌ Presigned URL test failed.")
        return
    
    print("\n✅ All tests passed! S3 upload should work correctly.")
    print("\nIf you're still having issues, check:")
    print("1. Browser console for JavaScript errors")
    print("2. Django logs for backend errors")
    print("3. Network tab in browser dev tools for HTTP errors")

if __name__ == "__main__":
    main() 