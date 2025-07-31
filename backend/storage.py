# storage.py - Create this file in your app directory
from storages.backends.s3boto3 import S3Boto3Storage
from django.conf import settings
import boto3
from botocore.config import Config


class OptimizedS3Storage(S3Boto3Storage):
    """
    Custom S3 storage with optimized multipart upload settings
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Configure optimized boto3 client
        self.config = Config(
            region_name=settings.AWS_S3_REGION_NAME,
            retries={'max_attempts': 3, 'mode': 'adaptive'},
            max_pool_connections=getattr(settings, 'AWS_S3_MAX_POOL_CONNECTIONS', 50)
        )
        
        # Override the client with optimized settings
        self._client = None
    
    @property
    def client(self):
        if self._client is None:
            self._client = boto3.client(
                's3',
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
                config=self.config
            )
        return self._client
    
    def _save(self, name, content):
        """
        Override save method to use optimized multipart upload
        """
        # Get file size
        content.seek(0, 2)  # Seek to end
        file_size = content.tell()
        content.seek(0)     # Seek back to beginning
        
        # Use multipart upload for files larger than threshold
        multipart_threshold = getattr(settings, 'AWS_S3_MULTIPART_THRESHOLD', 1024 * 25)
        
        if file_size > multipart_threshold:
            return self._save_multipart(name, content, file_size)
        else:
            return super()._save(name, content)
    
    def _save_multipart(self, name, content, file_size):
        """
        Save file using optimized multipart upload
        """
        from botocore.exceptions import ClientError
        
        try:
            # Configure transfer settings
            transfer_config = boto3.s3.transfer.TransferConfig(
                multipart_threshold=getattr(settings, 'AWS_S3_MULTIPART_THRESHOLD', 1024 * 25),
                max_concurrency=10,
                multipart_chunksize=getattr(settings, 'AWS_S3_MULTIPART_CHUNKSIZE', 1024 * 25),
                use_threads=True
            )
            
            # Perform the upload
            self.client.upload_fileobj(
                content,
                self.bucket_name,
                name,
                Config=transfer_config,
                ExtraArgs=self._get_write_parameters(name, content)
            )
            
            return name
            
        except ClientError as e:
            # Fall back to regular upload if multipart fails
            return super()._save(name, content)
    
    def _get_write_parameters(self, name, content):
        """
        Get parameters for S3 upload
        """
        params = {}
        
        # Set content type
        content_type = getattr(content, 'content_type', None)
        if content_type:
            params['ContentType'] = content_type
        
        # Set ACL if specified
        if hasattr(settings, 'AWS_DEFAULT_ACL') and settings.AWS_DEFAULT_ACL:
            params['ACL'] = settings.AWS_DEFAULT_ACL
            
        return params


class OptimizedVideoStorage(OptimizedS3Storage):
    """
    Specialized storage for video files with video-specific optimizations
    """
    location = 'videos'
    
    def get_alternative_name(self, file_root, file_ext):
        """
        Generate unique filename for videos to avoid conflicts
        """
        import uuid
        return f"{file_root}_{uuid.uuid4().hex[:8]}{file_ext}"

class OptimizedImageStorage(OptimizedS3Storage):
    """
    Specialized storage for images/thumbnails
    """
    location = 'images'