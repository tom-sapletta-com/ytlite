#!/usr/bin/env python3
"""
Simple YouTube uploader - focuses on what matters
"""

import os
import json
import pickle
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from rich.console import Console
import frontmatter
import click
from dotenv import load_dotenv

load_dotenv()

console = Console()

class SimpleYouTubeUploader:
    """Minimal YouTube uploader"""
    
    SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
    
    def __init__(self, credentials_file: str = "credentials/credentials.json"):
        self.credentials_file = credentials_file
        self.youtube = self._authenticate()
    
    def _authenticate(self):
        """Simple OAuth2 flow"""
        creds = None
        token_file = 'credentials/token.pickle'
        
        # Load existing token
        if os.path.exists(token_file):
            with open(token_file, 'rb') as token:
                creds = pickle.load(token)
        
        # Refresh or get new token
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_file):
                    console.print(f"[red]Error: {self.credentials_file} not found![/]")
                    console.print("[yellow]Please download your YouTube API credentials from Google Cloud Console[/]")
                    return None
                    
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, self.SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save token
            os.makedirs(os.path.dirname(token_file), exist_ok=True)
            with open(token_file, 'wb') as token:
                pickle.dump(creds, token)
        
        return build('youtube', 'v3', credentials=creds) if creds else None
    
    def upload_video(self, 
                     video_path: Path,
                     title: str,
                     description: str = "",
                     tags: list = None,
                     category: str = "28",  # Science & Technology
                     privacy: str = None) -> str:
        """Upload video with minimal config"""
        
        if not self.youtube:
            console.print("[red]YouTube authentication failed![/]")
            return None
            
        console.print(f"[yellow]Uploading:[/] {title}")
        
        # Use privacy from env if not specified
        if privacy is None:
            privacy = os.getenv("UPLOAD_PRIVACY", "unlisted")
        
        # Auto-generate description if empty
        if not description:
            description = self._generate_description(title, tags)
        
        body = {
            'snippet': {
                'title': title,
                'description': description,
                'tags': tags or [],
                'categoryId': category
            },
            'status': {
                'privacyStatus': privacy,
                'selfDeclaredMadeForKids': False,
            }
        }
        
        # Upload
        media = MediaFileUpload(
            str(video_path),
            chunksize=-1,
            resumable=True,
            mimetype='video/mp4'
        )
        
        try:
            request = self.youtube.videos().insert(
                part=','.join(body.keys()),
                body=body,
                media_body=media
            )
            
            response = request.execute()
            video_url = f"https://youtube.com/watch?v={response['id']}"
            
            console.print(f"[bold green]✓ Uploaded:[/] {video_url}")
            
            # Save URL for later reference
            self._save_upload_record(video_path, video_url, response['id'])
            
            return video_url
        except Exception as e:
            console.print(f"[red]Upload failed: {e}[/]")
            return None
    
    def upload_shorts(self, 
                      shorts_path: Path,
                      original_title: str) -> str:
        """Upload Shorts with #Shorts hashtag"""
        
        title = f"{original_title} #Shorts"
        description = f"""
{original_title} w 60 sekund!

#Shorts #Tech #Philosophy #Wetware #EdgeComputing

🧠 Subskrybuj, aby nie przegapić kolejnych przemyśleń!

🔗 Więcej:
→ Blog: https://wetware.dev
→ GitHub: https://github.com/tom-sapletta-com
→ LinkedIn: https://linkedin.com/in/tom-sapletta-com
        """
        
        return self.upload_video(
            shorts_path,
            title,
            description,
            tags=["shorts", "tech", "philosophy"],
            privacy=os.getenv("UPLOAD_PRIVACY", "public")
        )
    
    def _generate_description(self, title: str, tags: list) -> str:
        """Auto-generate engaging description"""
        hashtags = ' '.join([f"#{tag}" for tag in (tags or [])])
        
        return f"""
{title}

🧠 Subskrybuj, aby nie przegapić kolejnych przemyśleń!

🔗 Więcej:
→ Blog: https://wetware.dev
→ GitHub: https://github.com/tom-sapletta-com
→ LinkedIn: https://linkedin.com/in/tom-sapletta-com

{hashtags}

#AI #Technology #Future #Innovation #Programming #DevOps
        """
    
    def _save_upload_record(self, video_path: Path, url: str, video_id: str):
        """Keep track of uploads"""
        records_file = Path("output/upload_history.json")
        
        if records_file.exists():
            with open(records_file, 'r') as f:
                records = json.load(f)
        else:
            records = []
        
        records.append({
            "file": str(video_path),
            "url": url,
            "id": video_id,
            "uploaded_at": datetime.now().isoformat()
        })
        
        records_file.parent.mkdir(exist_ok=True)
        with open(records_file, 'w') as f:
            json.dump(records, f, indent=2)
    
    def batch_upload(self, folder: Path = Path("output")):
        """Upload all videos in folder"""
        videos = list((folder / "videos").glob("*.mp4"))
        shorts = list((folder / "shorts").glob("*.mp4"))
        
        console.print(f"[cyan]Found {len(videos)} videos and {len(shorts)} shorts[/]")
        
        # Upload main videos
        for video in videos:
            # Skip if already uploaded
            if self._is_uploaded(video):
                console.print(f"[dim]Skipping (already uploaded): {video.name}[/]")
                continue
            
            # Extract metadata from filename or use defaults
            title = video.stem.replace('_', ' ').title()
            
            # Try to load metadata from markdown
            md_file = Path(f"content/episodes/{video.stem}.md")
            if md_file.exists():
                with open(md_file, 'r') as f:
                    post = frontmatter.load(f)
                    title = post.metadata.get('title', title)
                    tags = post.metadata.get('tags', [])
            else:
                tags = ['tech', 'philosophy']
            
            self.upload_video(video, title, tags=tags)
        
        # Upload shorts
        for short in shorts:
            if self._is_uploaded(short):
                continue
            
            original_title = short.stem.replace('_short', '').replace('_', ' ').title()
            self.upload_shorts(short, original_title)
    
    def _is_uploaded(self, video_path: Path) -> bool:
        """Check if video was already uploaded"""
        records_file = Path("output/upload_history.json")
        if not records_file.exists():
            return False
        
        with open(records_file, 'r') as f:
            records = json.load(f)
        
        return any(r['file'] == str(video_path) for r in records)


@click.group()
def cli():
    """YouTube uploader CLI"""
    pass

@cli.command()
@click.option('--batch', is_flag=True, help='Upload all videos in output folder')
@cli.option('--folder', default='output', help='Folder to upload from')
def upload(batch, folder):
    """Upload videos to YouTube"""
    uploader = SimpleYouTubeUploader()
    
    if batch:
        uploader.batch_upload(Path(folder))
    else:
        console.print("[yellow]Use --batch flag to upload all videos[/]")

if __name__ == "__main__":
    cli()
