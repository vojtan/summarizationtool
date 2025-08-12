from datetime import datetime
from bs4 import BeautifulSoup
from pathlib import Path

class RssFeedUpdater:
    def __init__(self):
        self.feed_file = "rss_feed.xml"
    def update_feed(self, all_new_pdfs):        
        """Add new PDF items to the RSS feed"""
        if not all_new_pdfs:
            return
        
        # Load existing RSS feed
        if Path(self.feed_file).exists():
            with open(self.feed_file, 'r', encoding='utf-8') as f:
                rss_content = f.read()
        
        soup = BeautifulSoup(rss_content, 'xml')
        channel = soup.find('channel')

        for pdf in all_new_pdfs:
            item = soup.new_tag('item')
            title = soup.new_tag('title')
            title.string = pdf['source_title']
            link = soup.new_tag('link')
            link.string = pdf['url']
            description = soup.new_tag('description')
            description.string = pdf['summary']
            pub_date = soup.new_tag('pubDate')
            pub_date.string = datetime.now().strftime('%a, %d %b %Y %H:%M:%S +0000')

            item.append(title)
            item.append(link)
            item.append(pub_date)
            item.append(description)
            channel.append(item)

        # Save updated RSS feed
        with open(self.feed_file, 'w', encoding='utf-8') as f:
            f.write(str(soup))
        
