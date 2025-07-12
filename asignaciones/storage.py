"""
Azure Blob Storage backend for Django media files
"""

import os
from django.core.files.storage import Storage
from django.core.files.base import ContentFile
from django.conf import settings
from urllib.parse import urljoin
import logging

logger = logging.getLogger(__name__)

# Try to import Azure libraries, fallback gracefully if not available
try:
    from azure.storage.blob import BlobServiceClient
    from azure.identity import DefaultAzureCredential
    AZURE_AVAILABLE = True
except ImportError:
    logger.warning("Azure storage libraries not available, using local storage fallback")
    AZURE_AVAILABLE = False


class AzureBlobStorage(Storage):
    """
    Custom storage backend for Azure Blob Storage using managed identity
    """
    
    def __init__(self, option=None):
        self.account_name = getattr(settings, 'AZURE_STORAGE_ACCOUNT_NAME', None)
        self.container_name = getattr(settings, 'AZURE_STORAGE_CONTAINER_NAME', 'media')
        self.client = None
        
        if not AZURE_AVAILABLE or not self.account_name:
            logger.warning("Azure storage not available or not configured, falling back to local storage")
            return
            
        # Use managed identity for authentication
        account_url = f"https://{self.account_name}.blob.core.windows.net"
        
        try:
            credential = DefaultAzureCredential()
            self.client = BlobServiceClient(account_url=account_url, credential=credential)
            # Test the connection
            self.client.get_account_information()
            logger.info(f"Successfully connected to Azure Storage account: {self.account_name}")
        except Exception as e:
            logger.error(f"Failed to connect to Azure Storage: {e}")
            self.client = None
    
    def _save(self, name, content):
        """
        Save file to Azure Blob Storage
        """
        if not self.client:
            # Fallback to local file system
            return self._save_local(name, content)
            
        try:
            blob_client = self.client.get_blob_client(
                container=self.container_name, 
                blob=name
            )
            
            # Reset content position if it's a file-like object
            if hasattr(content, 'seek'):
                content.seek(0)
                
            blob_client.upload_blob(content, overwrite=True)
            logger.info(f"Successfully uploaded file: {name}")
            return name
            
        except Exception as e:
            logger.error(f"Failed to upload file {name} to Azure Storage: {e}")
            # Fallback to local storage
            return self._save_local(name, content)
    
    def _save_local(self, name, content):
        """
        Fallback to save file locally
        """
        media_root = getattr(settings, 'MEDIA_ROOT', 'media')
        full_path = os.path.join(media_root, name)
        
        # Create directories if they don't exist
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        with open(full_path, 'wb') as f:
            for chunk in content.chunks():
                f.write(chunk)
        
        return name
    
    def exists(self, name):
        """
        Check if file exists in Azure Blob Storage
        """
        if not self.client:
            # Check local filesystem
            media_root = getattr(settings, 'MEDIA_ROOT', 'media')
            return os.path.exists(os.path.join(media_root, name))
            
        try:
            blob_client = self.client.get_blob_client(
                container=self.container_name, 
                blob=name
            )
            return blob_client.exists()
        except Exception as e:
            logger.error(f"Error checking if file {name} exists: {e}")
            return False
    
    def url(self, name):
        """
        Return the URL for the file
        """
        if not self.client:
            # Return local URL
            media_url = getattr(settings, 'MEDIA_URL', '/media/')
            return urljoin(media_url, name)
            
        try:
            return f"https://{self.account_name}.blob.core.windows.net/{self.container_name}/{name}"
        except Exception as e:
            logger.error(f"Error generating URL for file {name}: {e}")
            # Fallback to local URL
            media_url = getattr(settings, 'MEDIA_URL', '/media/')
            return urljoin(media_url, name)
    
    def delete(self, name):
        """
        Delete file from Azure Blob Storage
        """
        if not self.client:
            # Delete from local filesystem
            media_root = getattr(settings, 'MEDIA_ROOT', 'media')
            file_path = os.path.join(media_root, name)
            if os.path.exists(file_path):
                os.remove(file_path)
            return
            
        try:
            blob_client = self.client.get_blob_client(
                container=self.container_name, 
                blob=name
            )
            blob_client.delete_blob()
            logger.info(f"Successfully deleted file: {name}")
        except Exception as e:
            logger.error(f"Failed to delete file {name} from Azure Storage: {e}")
    
    def size(self, name):
        """
        Return the size of the file
        """
        if not self.client:
            # Get size from local filesystem
            media_root = getattr(settings, 'MEDIA_ROOT', 'media')
            file_path = os.path.join(media_root, name)
            if os.path.exists(file_path):
                return os.path.getsize(file_path)
            return 0
            
        try:
            blob_client = self.client.get_blob_client(
                container=self.container_name, 
                blob=name
            )
            properties = blob_client.get_blob_properties()
            return properties.size
        except Exception as e:
            logger.error(f"Error getting size for file {name}: {e}")
            return 0
