"""
Module for publishing content to multiple platforms including WordPress, blogs, and social media.
Credentials are fetched from environment variables for security.
"""

import os
import requests
from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.posts import NewPost
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Publisher:
    def __init__(self):
        self.platforms = {}
        self.credentials = self.load_credentials()

    def load_credentials(self):
        """Load credentials for various platforms from environment variables."""
        credentials = {
            'wordpress': {
                'url': os.getenv('WORDPRESS_URL', ''),
                'username': os.getenv('WORDPRESS_USERNAME', ''),
                'password': os.getenv('WORDPRESS_PASSWORD', '')
            },
            'nextcloud': {
                'url': os.getenv('NEXTCLOUD_URL', ''),
                'username': os.getenv('NEXTCLOUD_USERNAME', ''),
                'password': os.getenv('NEXTCLOUD_PASSWORD', '')
            },
            # Add placeholders for other social media platforms
            'twitter': {
                'api_key': os.getenv('TWITTER_API_KEY', ''),
                'api_secret': os.getenv('TWITTER_API_SECRET', ''),
                'access_token': os.getenv('TWITTER_ACCESS_TOKEN', ''),
                'access_token_secret': os.getenv('TWITTER_ACCESS_TOKEN_SECRET', '')
            },
            'facebook': {
                'app_id': os.getenv('FACEBOOK_APP_ID', ''),
                'app_secret': os.getenv('FACEBOOK_APP_SECRET', ''),
                'access_token': os.getenv('FACEBOOK_ACCESS_TOKEN', '')
            }
        }
        return credentials

    def register_platform(self, platform_name, publish_function):
        """Register a platform with its publishing function."""
        self.platforms[platform_name] = publish_function

    def publish_to_wordpress(self, title, content, categories=None, tags=None):
        """Publish content to WordPress using XML-RPC."""
        wp_credentials = self.credentials.get('wordpress', {})
        if not all([wp_credentials['url'], wp_credentials['username'], wp_credentials['password']]):
            return False, "Missing WordPress credentials"

        try:
            wp = Client(wp_credentials['url'] + '/xmlrpc.php', wp_credentials['username'], wp_credentials['password'])
            post = WordPressPost()
            post.title = title
            post.content = content
            post.terms_names = {
                'post_tag': tags if tags else [],
                'category': categories if categories else []
            }
            post_id = wp.call(NewPost(post, True))
            return True, f"Successfully published to WordPress with ID {post_id}"
        except Exception as e:
            return False, f"Failed to publish to WordPress: {str(e)}"

    def publish_to_nextcloud(self, file_path, destination_path):
        """Upload a file to Nextcloud."""
        nc_credentials = self.credentials.get('nextcloud', {})
        if not all([nc_credentials['url'], nc_credentials['username'], nc_credentials['password']]):
            return False, "Missing Nextcloud credentials"

        try:
            from webdav3.client import Client
            options = {
                'webdav_hostname': nc_credentials['url'],
                'webdav_login': nc_credentials['username'],
                'webdav_password': nc_credentials['password']
            }
            client = Client(options)
            client.upload_sync(remote_path=destination_path, local_path=file_path)
            return True, f"Successfully uploaded to Nextcloud at {destination_path}"
        except Exception as e:
            return False, f"Failed to upload to Nextcloud: {str(e)}"

    def publish_content(self, platforms, title, content, media_files=None, categories=None, tags=None):
        """Publish content to multiple specified platforms."""
        results = []
        for platform in platforms:
            if platform == 'wordpress':
                success, message = self.publish_to_wordpress(title, content, categories, tags)
                results.append({'platform': 'WordPress', 'success': success, 'message': message})
            elif platform == 'nextcloud' and media_files:
                for file_path, dest_path in media_files.items():
                    success, message = self.publish_to_nextcloud(file_path, dest_path)
                    results.append({'platform': 'Nextcloud', 'success': success, 'message': message})
            # Add logic for other platforms here
        return results

if __name__ == "__main__":
    publisher = Publisher()
    # Example usage
    result = publisher.publish_content(
        platforms=['wordpress'],
        title="Test Post from ytlite",
        content="This is a test post published from ytlite application.",
        categories=["Test"],
        tags=["test", "ytlite"]
    )
    for res in result:
        print(f"{res['platform']}: {res['message']}")
