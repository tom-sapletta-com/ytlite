#!/usr/bin/env python3
"""
Daily automation scheduler for YTLite
"""

import schedule
import time
import random
from datetime import datetime
from pathlib import Path
from rich.console import Console
from dotenv import load_dotenv
import os

from ytlite import YTLite
from youtube_uploader import SimpleYouTubeUploader

load_dotenv()

console = Console()

class ContentScheduler:
    """Automated content generation and publishing"""
    
    def __init__(self):
        self.generator = YTLite()
        self.uploader = SimpleYouTubeUploader()
        self.topics = self._load_topics()
    
    def _load_topics(self) -> list:
        """Load topic ideas or use defaults"""
        # Default topics for different themes
        return {
            "wetware": [
                "Jak social media programuje twój mózg",
                "Dlaczego scrolling to nowy nikotynizm", 
                "Twój mózg vs algorytm: kto kogo hakuje",
                "Digital dopamine: chemiczny hak aplikacji",
                "Notification anxiety: nowa choroba XXI wieku"
            ],
            "philosophy": [
                "Paradoks wyboru w erze AI",
                "Czy Siri rozumie samotność?",
                "Digital detox czy digital death?",
                "Minimalizm cyfrowy vs cyfrowe ubóstwo",
                "Czas przestać liczyć czas i zacząć liczyć chwile?"
            ],
            "tech": [
                "Edge computing w kuchni", 
                "Dlaczego twój toster potrzebuje update'u",
                "IoT czy Internet of Threats?",
                "Mikroservisy vs distributed monolith",
                "Blockchain wszystkiego: hype czy przyszłość?"
            ]
        }
    
    def generate_daily_content(self):
        """Generate content for today"""
        console.print("[bold cyan]🤖 Generating daily content...[/]")
        
        # Pick random theme and topic
        theme = random.choice(list(self.topics.keys()))
        prompt = random.choice(self.topics[theme])
        
        today = datetime.now()
        
        # Generate content based on theme
        if theme == "philosophy":
            content = self._create_philosophical_content(prompt, today)
        elif theme == "wetware":
            content = self._create_wetware_content(prompt, today)
        else:  # tech
            content = self._create_tech_content(prompt, today)
        
        # Save content
        filename = Path(f"content/episodes/auto_{today.strftime('%Y%m%d')}_{theme}.md")
        filename.parent.mkdir(parents=True, exist_ok=True)
        filename.write_text(content, encoding='utf-8')
        
        console.print(f"[green]📝 Content saved: {filename}[/]")
        
        # Generate video
        video_path = self.generator.create_video_from_markdown(filename)
        
        # Create shorts if enabled
        if os.getenv("GENERATE_SHORTS", "true").lower() == "true":
            shorts_path = self.generator.create_shorts_version(video_path)
        
        # Upload if auto-upload is enabled
        if os.getenv("AUTO_UPLOAD", "false").lower() == "true":
            with open(filename, 'r') as f:
                import frontmatter
                post = frontmatter.load(f)
                title = post.metadata.get('title', prompt)
                tags = post.metadata.get('tags', [theme])
            
            self.uploader.upload_video(video_path, title, tags=tags)
            
            if os.getenv("GENERATE_SHORTS", "true").lower() == "true":
                self.uploader.upload_shorts(shorts_path, title)
        
        console.print("[bold green]✅ Daily content complete![/]")
    
    def _create_philosophical_content(self, prompt: str, date: datetime) -> str:
        """Create philosophical reflection content"""
        return f"""---
title: "{prompt}"
date: {date.strftime('%Y-%m-%d')}
theme: philosophy
tags: [filozofia, życie, technologia, refleksja]
---

{prompt}

To pytanie, które zadaję sobie codziennie.

Żyjemy w czasach, gdy maszyny rozumieją nas lepiej niż my sami siebie. Algorytmy przewidują nasze wybory, zanim je podejmiemy.

Może czas przestać pytać "czy" i zacząć pytać "jak"?

A ty jak myślisz? Daj znać w komentarzach.
"""
    
    def _create_wetware_content(self, prompt: str, date: datetime) -> str:
        """Create wetware/brain-tech content"""
        return f"""---
title: "{prompt}"
date: {date.strftime('%Y-%m-%d')}
theme: wetware
tags: [wetware, mózg, technologia, cyborg]
---

{prompt}

Twój mózg to najbardziej zaawansowany komputer, jaki znamy.

Każdego dnia programujesz swój wetware przez to, co czytasz, oglądasz i myślisz. Media społecznościowe to IDE dla twojego mózgu.

🤯 Pytanie brzmi: kto pisze kod, który wykonujesz? Ty czy algorytm?

Welcome to the wetware revolution.
"""
    
    def _create_tech_content(self, prompt: str, date: datetime) -> str:
        """Create technical content"""
        return f"""---
title: "{prompt}"
date: {date.strftime('%Y-%m-%d')}
theme: tech
tags: [tech, innovation, future, development]
---

{prompt}

Here's what you need to know:

Technology evolves faster than our ability to understand it. But that's exactly what makes it exciting.

⚡ Key insight: The future doesn't wait for permission.

Are you building the future, or is the future building you?
"""
    
    def run_scheduler(self):
        """Run the automated scheduler"""
        
        # Get schedule time from environment or default
        schedule_time = os.getenv("SCHEDULE_TIME", "09:00")
        
        # Schedule daily content
        schedule.every().day.at(schedule_time).do(self.generate_daily_content)
        
        console.print(f"[bold green]📅 Scheduler started![/]")
        console.print(f"Daily content will be generated at: [yellow]{schedule_time}[/]")
        console.print(f"Next run: [cyan]{schedule.next_run()}[/]")
        console.print("Press Ctrl+C to stop")
        
        while True:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except KeyboardInterrupt:
                console.print("\n[yellow]Scheduler stopped by user[/]")
                break

if __name__ == "__main__":
    scheduler = ContentScheduler()
    scheduler.run_scheduler()
