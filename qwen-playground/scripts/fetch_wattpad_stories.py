# Fetch stories from Wattpad using Wattpad API

import requests
import sys
import json
from pathlib import Path
from bs4 import BeautifulSoup

def get_book_by_id(story_id: str, session: requests.Session) -> dict | None:
    """
    Get book data by story ID using Wattpad API v3.
    Returns JSON data or None if not found.
    """
    url = f"https://www.wattpad.com/api/v3/stories/{story_id}"
    params = {
        'fields': 'id,title,description,url,cover,isPaywalled,user(name,username,avatar),lastPublishedPart,parts(id,title,text_url),tags'
    }
    headers = {
        'Accept': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }
    
    try:
        response = session.get(url, params=params, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        if response.status_code == 404:
            return None
        print(f"Error fetching book by ID: {e}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Error fetching book by ID: {e}", file=sys.stderr)
        return None


def get_book_by_part_id(part_id: str, session: requests.Session) -> dict | None:
    """
    Get book data by part ID using Wattpad API v4.
    Returns JSON data or None if not found.
    """
    url = f"https://www.wattpad.com/v4/parts/{part_id}"
    params = {
        'fields': 'text_url,group(id,title,description,isPaywalled,url,cover,user(name,username,avatar),lastPublishedPart,parts(id,title,text_url),tags)'
    }
    headers = {
        'Accept': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }
    
    try:
        response = session.get(url, params=params, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        # Extract the group (book) data from the response
        return data.get('group')
    except requests.exceptions.HTTPError as e:
        if response.status_code == 404:
            return None
        print(f"Error fetching book by part ID: {e}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Error fetching book by part ID: {e}", file=sys.stderr)
        return None


def html_to_text(html_content: str) -> str:
    """
    Convert HTML content to plain text.
    Removes HTML tags and extracts readable text.
    """
    if not html_content:
        return ""
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Remove script and style elements
    for script in soup(["script", "style"]):
        script.decompose()
    
    # Get text and clean it up
    text = soup.get_text()
    
    # Clean up whitespace
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = '\n'.join(chunk for chunk in chunks if chunk)
    
    return text


def fetch_part_text(text_url: str, session: requests.Session, parse_html: bool = True) -> str | None:
    """
    Fetch the actual text content of a story part.
    Returns the plain text content (parsed from HTML) or None if failed.
    
    Args:
        text_url: URL to fetch the text from
        session: Requests session object
        parse_html: If True, parse HTML to plain text. If False, return raw HTML.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    }
    
    try:
        response = session.get(text_url, headers=headers, timeout=30)
        response.raise_for_status()
        html_content = response.text
        
        if parse_html:
            return html_to_text(html_content)
        else:
            return html_content
    except Exception as e:
        print(f"Error fetching part text from {text_url}: {e}", file=sys.stderr)
        return None


def fetch_wattpad_story(story_id: str, include_text: bool = False, parse_html: bool = True) -> dict:
    """
    Fetch a story from Wattpad by story ID or part ID.
    Uses Wattpad's API to get JSON data instead of scraping HTML.
    
    Args:
        story_id: Story ID or part ID
        include_text: If True, also fetch the text content of each part
        parse_html: If True, parse HTML to plain text. If False, return raw HTML.
    
    Returns:
        Dictionary containing story data in JSON format
    """
    session = requests.Session()
    
    # Try to get book by story ID first
    book = get_book_by_id(story_id, session)
    
    # If that fails, try to get book by part ID
    if not book:
        book = get_book_by_part_id(story_id, session)
    
    if not book:
        raise ValueError(f"Story or part with ID '{story_id}' not found")
    
    # If include_text is True, fetch the text content for each part
    if include_text and 'parts' in book:
        parts_with_text = []
        for part in book.get('parts', []):
            if 'text_url' in part and 'text' in part['text_url']:
                text_content = fetch_part_text(part['text_url']['text'], session, parse_html=parse_html)
                part_data = {
                    'id': part.get('id'),
                    'title': part.get('title'),
                    'text': text_content
                }
                parts_with_text.append(part_data)
            else:
                parts_with_text.append(part)
        book['parts'] = parts_with_text
    
    return book


def save_story_to_files(story: dict, output_dir: str | Path, story_id: str):
    """
    Save story data to files in the output directory.
    Creates a directory structure and saves JSON metadata and text files.
    
    Args:
        story: Story data dictionary
        output_dir: Output directory path
        story_id: Story ID for naming files
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Create a subdirectory for this story
    story_dir = output_path / f"story_{story_id}"
    story_dir.mkdir(exist_ok=True)
    
    # Save full JSON metadata
    json_file = story_dir / "metadata.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(story, f, indent=2, ensure_ascii=False)
    print(f"Saved metadata to {json_file}", file=sys.stderr)
    
    # Save individual parts as text files if text content is available
    if 'parts' in story and story['parts']:
        parts_dir = story_dir / "parts"
        parts_dir.mkdir(exist_ok=True)
        
        for idx, part in enumerate(story['parts'], 1):
            if 'text' in part and part['text']:
                # Create a safe filename from the part title or use index
                if part.get('title'):
                    # Sanitize filename
                    safe_title = "".join(c for c in part['title'] if c.isalnum() or c in (' ', '-', '_')).strip()
                    safe_title = safe_title.replace(' ', '_')[:50]  # Limit length
                    filename = f"{idx:03d}_{safe_title}.txt"
                else:
                    filename = f"{idx:03d}_part_{part.get('id', idx)}.txt"
                
                part_file = parts_dir / filename
                with open(part_file, 'w', encoding='utf-8') as f:
                    f.write(part['text'])
                print(f"Saved part {idx} to {part_file}", file=sys.stderr)
    
    # Save a combined text file with all parts
    if 'parts' in story and story['parts']:
        combined_file = story_dir / "combined.txt"
        with open(combined_file, 'w', encoding='utf-8') as f:
            f.write(f"Title: {story.get('title', 'Unknown')}\n")
            f.write(f"Author: {story.get('user', {}).get('name', 'Unknown')}\n")
            f.write(f"Description: {story.get('description', '')}\n")
            f.write("=" * 80 + "\n\n")
            
            for idx, part in enumerate(story['parts'], 1):
                if 'text' in part and part['text']:
                    f.write(f"\n{'=' * 80}\n")
                    f.write(f"Part {idx}: {part.get('title', 'Untitled')}\n")
                    f.write(f"{'=' * 80}\n\n")
                    f.write(part['text'])
                    f.write("\n\n")
        
        print(f"Saved combined text to {combined_file}", file=sys.stderr)
    
    return story_dir

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Fetch Wattpad story data as JSON')
    parser.add_argument('story_id', help='Story ID or part ID')
    parser.add_argument('--include-text', action='store_true', 
                       help='Include the full text content of each part (slower)')
    parser.add_argument('--output-dir', type=str, default='outputs',
                       help='Output directory to save story files (default: outputs)')
    parser.add_argument('--save-files', action='store_true',
                       help='Save story to files in output directory')
    parser.add_argument('--print', action='store_true',
                       help='Print JSON output to stdout')
    
    args = parser.parse_args()
    
    try:
        story = fetch_wattpad_story(
            args.story_id, 
            include_text=args.include_text,
            parse_html=args.print
        )

        
        if args.print:
            print(json.dumps(story, indent=2, ensure_ascii=False))
        else:
            output_dir = save_story_to_files(story, args.output_dir, args.story_id)
            print(f"\nStory saved to: {output_dir}", file=sys.stderr)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)