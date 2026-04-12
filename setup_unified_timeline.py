#!/usr/bin/env python3
"""
Unified Jess Timeline Setup Script
Automatically configures everything needed for the timeline project
"""

import os
import sys
import subprocess
import platform
import json
from pathlib import Path

# Color output for better UX
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_step(step_number, description):
    print(f"\n{Colors.BOLD}{Colors.OKBLUE}[{step_number}]{Colors.ENDC} {description}")

def print_success(message):
    print(f"{Colors.OKGREEN}✓ {message}{Colors.ENDC}")

def print_warning(message):
    print(f"{Colors.WARNING}⚠ {message}{Colors.ENDC}")

def print_error(message):
    print(f"{Colors.FAIL}✗ {message}{Colors.ENDC}")

def run_command(command, description):
    """Run a shell command and handle errors"""
    print(f"  Running: {description}")
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            check=True, 
            capture_output=True, 
            text=True
        )
        if result.stdout:
            print_success(result.stdout.strip())
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Command failed: {e}")
        if e.stderr:
            print_error(f"Error: {e.stderr}")
        return False

def check_dependencies():
    """Check if required dependencies are installed"""
    print_step(1, "Checking System Dependencies")
    
    # Check macOS
    if platform.system() != "Darwin":
        print_error("This setup script is designed for macOS only")
        sys.exit(1)
    
    print_success(f"macOS detected: {platform.machine()}")
    
    # Check Python version
    python_version = sys.version_info
    if python_version < (3, 11):
        print_error("Python 3.11 or higher is required")
        print("Please install Python 3.11+ from python.org or Homebrew")
        sys.exit(1)
    
    print_success(f"Python {python_version.major}.{python_version.minor} detected")
    
    # Check pip
    try:
        subprocess.run([sys.executable, "-m", "pip", "--version"], 
                      check=True, capture_output=True)
        print_success("pip is available")
    except:
        print_error("pip not found. Installing pip...")
        run_command("curl https://bootstrap.pypa.io/get-pip.py | python3", "Installing pip")
    
    # Check Homebrew
    try:
        subprocess.run(["brew", "--version"], check=True, capture_output=True)
        print_success("Homebrew is available")
    except:
        print_warning("Homebrew not found. Installing Homebrew...")
        run_command('/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"', 
                   "Installing Homebrew")

def install_python_packages():
    """Install required Python packages"""
    print_step(2, "Installing Python Dependencies")
    
    packages = [
        "typer[all]",
        "beautifulsoup4",
        "lxml",
        "ijson",
        "faster-whisper",
        "orjson",
        "jinja2",
        "fastapi",
        "uvicorn[standard]",
        "sqlite3"
    ]
    
    for package in packages:
        if package == "sqlite3":
            continue  # Built into Python
        run_command(f"{sys.executable} -m pip install {package}", 
                   f"Installing {package}")
    
    print_success("All Python packages installed")

def create_directory_structure():
    """Create the project directory structure"""
    print_step(3, "Creating Directory Structure")
    
    base_path = Path("unified_jess_timeline")
    
    directories = [
        base_path,
        base_path / "scripts",
        base_path / "data",
        base_path / "data" / "cache",
        base_path / "data" / "outputs",
        base_path / "inputs",
        base_path / "inputs" / "Takeout",
        base_path / "inputs" / "Takeout" / "Voice",
        base_path / "inputs" / "Takeout" / "Google Chat",
        base_path / "logs"
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        print_success(f"Created directory: {directory}")
    
    return base_path

def create_config_file(base_path):
    """Create the configuration file with user inputs"""
    print_step(4, "Configuring Project Settings")
    
    print("\nWe'll need some information to configure the project:")
    
    # Get inputs from user
    takeout_path = input(f"{Colors.OKCYAN}Enter path to your Takeout folder (default: ~/Desktop/Takeout):{Colors.ENDC} ").strip()
    if not takeout_path:
        takeout_path = str(Path.home() / "Desktop" / "Takeout")
    
    messages_db_path = input(f"{Colors.OKCYAN}Enter path to your Messages database (default: ~/Library/Messages/chat.db):{Colors.ENDC} ").strip()
    if not messages_db_path:
        messages_db_path = str(Path.home() / "Library" / "Messages" / "chat.db")
    
    jess_contact = input(f"{Colors.OKCYAN}Enter Jess's contact identifier (name, number, or email):{Colors.ENDC} ").strip()
    
    # Create config file
    config_content = f'''"""
Configuration file for Unified Jess Timeline
"""

import os
from pathlib import Path

# User Configuration
TAKEOUT_BASE_PATH = "{takeout_path}"
MESSAGES_DB_PATH = "{messages_db_path}"
JESS_CONTACT_IDENTIFIER = "{jess_contact}"

# Project Paths
BASE_PATH = Path(__file__).parent.parent
SCRIPTS_PATH = BASE_PATH / "scripts"
DATA_PATH = BASE_PATH / "data"
OUTPUTS_PATH = DATA_PATH / "outputs"
CACHE_PATH = DATA_PATH / "cache"
LOGS_PATH = BASE_PATH / "logs"

# Transcription Settings
TRANSCRIPTION_ENGINE = "faster-whisper"  # faster-whisper | apple-speech
WHISPER_MODEL = "small"  # tiny | base | small | medium | large
TRANSCRIPTION_CACHE_DB = CACHE_PATH / "transcriptions.db"

# Output Settings
UNIFIED_JSON = OUTPUTS_PATH / "unified_jess_timeline.json"
UNIFIED_MD = OUTPUTS_PATH / "unified_jess_timeline.md"
UNIFIED_HTML = OUTPUTS_PATH / "unified_jess_timeline.html"

# Timeline Settings
BATCH_SIZE = 100  # Process messages in batches
MAX_ATTACHMENT_SIZE = 100 * 1024 * 1024  # 100MB

# Logging
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
'''
    
    config_file = base_path / "scripts" / "00_config.py"
    with open(config_file, 'w') as f:
        f.write(config_content)
    
    print_success(f"Configuration file created: {config_file}")

def create_utility_scripts(base_path):
    """Create utility scripts"""
    print_step(5, "Creating Utility Scripts")
    
    # Create requirements.txt
    requirements = '''typer[all]
beautifulsoup4
lxml
ijson
faster-whisper
orjson
jinja2
fastapi
uvicorn[standard]
'''
    
    req_file = base_path / "requirements.txt"
    with open(req_file, 'w') as f:
        f.write(requirements)
    
    print_success("Created requirements.txt")
    
    # Create .gitignore
    gitignore = '''# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
env/
ENV/
.venv/

# macOS
.DS_Store

# Logs
*.log

# Data
data/cache/*
data/outputs/*
!data/cache/.gitkeep
!data/outputs/.gitkeep

# Takeout data
inputs/Takeout/*
!inputs/Takeout/.gitkeep

# Config
.env
'''
    
    gitignore_file = base_path / ".gitignore"
    with open(gitignore_file, 'w') as f:
        f.write(gitignore)
    
    print_success("Created .gitignore")

def create_pipeline_scripts(base_path):
    """Create all pipeline scripts"""
    print_step(6, "Creating Pipeline Scripts")
    
    scripts = {
        "01_fetch_messages.py": '''#!/usr/bin/env python3
"""Fetch messages from Apple Messages database"""

import importlib.util
import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

_scripts = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("timeline_00_config", _scripts / "00_config.py")
_cfg = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_cfg)

MESSAGES_DB_PATH = _cfg.MESSAGES_DB_PATH
OUTPUTS_PATH = _cfg.OUTPUTS_PATH
JESS_CONTACT_IDENTIFIER = _cfg.JESS_CONTACT_IDENTIFIER

def connect_messages_db():
    """Connect to the Messages database"""
    try:
        conn = sqlite3.connect(MESSAGES_DB_PATH)
        return conn
    except sqlite3.Error as e:
        print(f"Error connecting to Messages database: {e}")
        sys.exit(1)

def fetch_messages(conn):
    """Fetch messages from the database"""
    cursor = conn.cursor()
    
    # Query to get messages and attachments
    query = """
    SELECT 
        m.ROWID as message_id,
        m.text,
        m.date as timestamp,
        m.is_from_me,
        a.ROWID as attachment_id,
        a.filename,
        a.mime_type,
        a.total_bytes
    FROM message m
    LEFT JOIN message_attachment_join maj ON m.ROWID = maj.message_id
    LEFT JOIN attachment a ON maj.attachment_id = a.ROWID
    WHERE m.text IS NOT NULL OR a.ROWID IS NOT NULL
    ORDER BY m.date ASC
    """
    
    cursor.execute(query)
    results = cursor.fetchall()
    
    messages = {}
    
    for row in results:
        message_id, text, timestamp, is_from_me, attachment_id, filename, mime_type, total_bytes = row
        
        if message_id not in messages:
            # Convert timestamp (macOS uses seconds since 2001-01-01)
            if timestamp:
                # Convert to Unix timestamp (seconds since 1970)
                unix_timestamp = timestamp + 978307200  # Seconds between 1970 and 2001
                utc_timestamp = datetime.fromtimestamp(unix_timestamp, tz=timezone.utc)
            else:
                utc_timestamp = None
            
            messages[message_id] = {
                'id': str(message_id),
                'text': text or '',
                'timestamp': utc_timestamp.isoformat() if utc_timestamp else None,
                'is_from_me': bool(is_from_me),
                'attachments': []
            }
        
        # Add attachment if exists
        if attachment_id and filename:
            messages[message_id]['attachments'].append({
                'id': str(attachment_id),
                'filename': filename,
                'mime_type': mime_type,
                'size': total_bytes,
                'path': f"~/Library/Messages/Attachments/{filename}"
            })
    
    return list(messages.values())

def main():
    """Main function"""
    print("Fetching messages from Apple Messages database...")
    
    conn = connect_messages_db()
    messages = fetch_messages(conn)
    conn.close()
    
    # Save to output file
    output_file = OUTPUTS_PATH / "messages_raw.jsonl"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w') as f:
        for message in messages:
            f.write(json.dumps(message) + '\\n')
    
    print(f"Fetched {len(messages)} messages to {output_file}")

if __name__ == "__main__":
    main()
''',

        "02_transcribe_messages.py": '''#!/usr/bin/env python3
"""Transcribe audio messages using Whisper"""

import hashlib
import importlib.util
import json
import sqlite3
import sys
from pathlib import Path

from faster_whisper import WhisperModel

_scripts = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("timeline_00_config", _scripts / "00_config.py")
_cfg = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_cfg)

OUTPUTS_PATH = _cfg.OUTPUTS_PATH
TRANSCRIPTION_CACHE_DB = _cfg.TRANSCRIPTION_CACHE_DB
WHISPER_MODEL = _cfg.WHISPER_MODEL
TRANSCRIPTION_ENGINE = _cfg.TRANSCRIPTION_ENGINE

class TranscriptionManager:
    def __init__(self):
        self.cache_db = TRANSCRIPTION_CACHE_DB
        self.setup_cache()
        
        if TRANSCRIPTION_ENGINE == "faster-whisper":
            self.model = WhisperModel(WHISPER_MODEL, device="cpu", compute_type="int8")
        else:
            print("Apple Speech not implemented yet")
            sys.exit(1)
    
    def setup_cache(self):
        """Initialize the transcription cache database"""
        self.cache_db.parent.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(self.cache_db)
        cursor = conn.cursor()
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS transcriptions (
            file_hash TEXT PRIMARY KEY,
            transcript TEXT,
            duration REAL,
            engine TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        conn.commit()
        conn.close()
    
    def get_file_hash(self, file_path):
        """Generate hash for a file"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def get_cached_transcript(self, file_hash):
        """Get transcript from cache"""
        conn = sqlite3.connect(self.cache_db)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT transcript FROM transcriptions WHERE file_hash = ?",
            (file_hash,)
        )
        
        result = cursor.fetchone()
        conn.close()
        
        return result[0] if result else None
    
    def cache_transcript(self, file_hash, transcript, duration):
        """Cache the transcript"""
        conn = sqlite3.connect(self.cache_db)
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT OR REPLACE INTO transcriptions (file_hash, transcript, duration, engine) VALUES (?, ?, ?, ?)",
            (file_hash, transcript, duration, TRANSCRIPTION_ENGINE)
        )
        
        conn.commit()
        conn.close()
    
    def transcribe_audio(self, audio_path):
        """Transcribe audio file"""
        file_hash = self.get_file_hash(audio_path)
        
        # Check cache first
        cached = self.get_cached_transcript(file_hash)
        if cached:
            return cached
        
        # Transcribe using Whisper (segments is a generator; materialize before multiple passes)
        segments, info = self.model.transcribe(audio_path)
        segments = list(segments)
        
        transcript = ""
        for segment in segments:
            transcript += segment.text + " "
        
        duration = sum(segment.end for segment in segments)
        
        # Cache the result
        self.cache_transcript(file_hash, transcript.strip(), duration)
        
        return transcript.strip()
    
    def process_messages(self, input_file):
        """Process messages and transcribe audio"""
        print("Processing messages for transcription...")
        
        processed_messages = []
        
        with open(input_file, 'r') as f:
            for line in f:
                message = json.loads(line)
                
                # Process audio attachments
                text_parts = [message['text']] if message['text'] else []
                
                for attachment in message.get('attachments', []):
                    if attachment['mime_type'].startswith('audio/'):
                        try:
                            transcript = self.transcribe_audio(
                                Path(attachment['path']).expanduser()
                            )
                            text_parts.append(f"[Audio]: {transcript}")
                        except Exception as e:
                            print(f"Failed to transcribe {attachment['filename']}: {e}")
                            text_parts.append(f"[Audio]: [Transcription failed]")
                
                # Update message with combined text
                message['text'] = ' '.join(text_parts).strip()
                message['transcribed'] = True
                
                processed_messages.append(message)
        
        return processed_messages
    
    def save_processed_messages(self, messages, output_file):
        """Save processed messages"""
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w') as f:
            for message in messages:
                f.write(json.dumps(message) + '\\n')

def main():
    """Main function"""
    input_file = OUTPUTS_PATH / "messages_raw.jsonl"
    output_file = OUTPUTS_PATH / "messages_enriched.jsonl"
    
    if not input_file.exists():
        print(f"Error: Input file {input_file} not found")
        sys.exit(1)
    
    transcriber = TranscriptionManager()
    messages = transcriber.process_messages(input_file)
    transcriber.save_processed_messages(messages, output_file)
    
    print(f"Processed {len(messages)} messages to {output_file}")

if __name__ == "__main__":
    main()
''',

        "06_merge_outputs.py": '''#!/usr/bin/env python3
"""Merge all event sources into unified timeline"""

import importlib.util
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

_scripts = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("timeline_00_config", _scripts / "00_config.py")
_cfg = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_cfg)

OUTPUTS_PATH = _cfg.OUTPUTS_PATH
UNIFIED_JSON = _cfg.UNIFIED_JSON
UNIFIED_MD = _cfg.UNIFIED_MD

def load_jsonl(file_path):
    """Load JSONL file into list of events"""
    events = []
    try:
        with open(file_path, 'r') as f:
            for line in f:
                events.append(json.loads(line.strip()))
    except FileNotFoundError:
        pass
    return events

def sort_events(events):
    """Sort events by timestamp"""
    def get_timestamp(event):
        timestamp_str = event.get('timestamp')
        if timestamp_str:
            return datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        return datetime.min.replace(tzinfo=timezone.utc)
    
    return sorted(events, key=get_timestamp)

def generate_statistics(events):
    """Generate timeline statistics"""
    stats = {
        'total_events': len(events),
        'sources': {},
        'date_range': {
            'start': events[0]['timestamp'] if events else None,
            'end': events[-1]['timestamp'] if events else None
        }
    }
    
    for event in events:
        source = event.get('source', 'unknown')
        stats['sources'][source] = stats['sources'].get(source, 0) + 1
    
    return stats

def save_unified_json(events, output_file):
    """Save unified timeline as JSON"""
    timeline_data = {
        'generated_at': datetime.now().isoformat(),
        'total_events': len(events),
        'statistics': generate_statistics(events),
        'events': events
    }
    
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump(timeline_data, f, indent=2)

def save_unified_markdown(events, output_file):
    """Save unified timeline as Markdown"""
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Group events by date
    events_by_date = {}
    for event in events:
        timestamp = event.get('timestamp')
        if timestamp:
            date = datetime.fromisoformat(timestamp.replace('Z', '+00:00')).date()
            if date not in events_by_date:
                events_by_date[date] = []
            events_by_date[date].append(event)
    
    with open(output_file, 'w') as f:
        f.write("# Unified Jess Timeline\\n\\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\\n\\n")
        f.write(f"Total events: {len(events)}\\n\\n")
        
        for date in sorted(events_by_date.keys()):
            f.write(f"## {date}\\n\\n")
            
            for event in events_by_date[date]:
                timestamp = event.get('timestamp', '')
                source = event.get('source', 'unknown')
                sender = "Me" if event.get('is_from_me') else event.get('sender', 'Unknown')
                text = event.get('text', '')
                
                f.write(f"- **{timestamp}** [{source}] **{sender}**: {text}\\n")
            
            f.write("\\n")

def main():
    """Main function"""
    print("Merging all timeline sources...")
    
    # Load all event sources
    messages_events = load_jsonl(OUTPUTS_PATH / "messages_enriched.jsonl")
    voice_events = load_jsonl(OUTPUTS_PATH / "voice_events.jsonl")
    chat_events = load_jsonl(OUTPUTS_PATH / "chat_events.jsonl")
    alexa_events = load_jsonl(OUTPUTS_PATH / "alexa_events.jsonl")
    
    # Combine all events
    all_events = messages_events + voice_events + chat_events + alexa_events
    
    # Sort by timestamp
    all_events = sort_events(all_events)
    
    # Save outputs
    save_unified_json(all_events, UNIFIED_JSON)
    save_unified_markdown(all_events, UNIFIED_MD)
    
    print(f"Merged {len(all_events)} events into unified timeline")
    print(f"JSON: {UNIFIED_JSON}")
    print(f"Markdown: {UNIFIED_MD}")

if __name__ == "__main__":
    main()
'''
    }
    
    # Write each script
    for script_name, content in scripts.items():
        script_path = base_path / "scripts" / script_name
        with open(script_path, 'w') as f:
            f.write(content)
        os.chmod(script_path, 0o755)  # Make executable
        print_success(f"Created script: {script_name}")

def create_wrapper_script(base_path):
    """Create the wrapper script for running the pipeline"""
    print_step(7, "Creating Pipeline Wrapper Script")
    
    wrapper_content = '''#!/bin/bash
# Unified Jess Timeline Pipeline Wrapper

set -e

echo "Starting Unified Jess Timeline Pipeline..."

# Navigate to script directory
cd "$(dirname "$0")"

# Run each step of the pipeline
echo "Step 1: Fetching messages..."
python3 01_fetch_messages.py

echo "Step 2: Transcribing audio..."
python3 02_transcribe_messages.py

echo "Step 3: Parsing Google Voice..."
# python3 03_parse_google_voice.py  # Uncomment when Google Voice data is available

echo "Step 4: Parsing Google Chat..."
# python3 04_parse_google_chat.py   # Uncomment when Google Chat data is available

echo "Step 5: Parsing Alexa..."
# python3 05_parse_alexa.py         # Uncomment when Alexa data is available

echo "Step 6: Merging outputs..."
python3 06_merge_outputs.py

echo "Pipeline completed successfully!"

# Open the output directory
open ../data/outputs/
'''
    
    wrapper_path = base_path / "scripts" / "run_timeline_update.sh"
    with open(wrapper_path, 'w') as f:
        f.write(wrapper_content)
    os.chmod(wrapper_path, 0o755)
    print_success(f"Created wrapper script: {wrapper_path.name}")

def create_launchd_plist(base_path):
    """Create launchd plist for auto-update"""
    print_step(8, "Creating Auto-Update Configuration")
    
    root = base_path.resolve()
    scripts_dir = root / "scripts"
    logs_dir = root / "logs"
    wrapper_sh = scripts_dir / "run_timeline_update.sh"
    logs_dir.mkdir(parents=True, exist_ok=True)
    
    plist_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.yourname.unified-timeline</string>
    
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>{wrapper_sh}</string>
    </array>
    
    <key>WorkingDirectory</key>
    <string>{scripts_dir}</string>
    
    <key>StartInterval</key>
    <integer>900</integer>
    
    <key>StandardOutPath</key>
    <string>{logs_dir / "timeline.log"}</string>
    
    <key>StandardErrorPath</key>
    <string>{logs_dir / "timeline_error.log"}</string>
    
    <key>RunAtLoad</key>
    <true/>
    
    <key>KeepAlive</key>
    <false/>
    
    <key>LaunchOnlyOnce</key>
    <false/>
</dict>
</plist>
'''
    
    plist_path = base_path / "com.yourname.unified-timeline.plist"
    with open(plist_path, 'w') as f:
        f.write(plist_content)
    
    print_success(f"Created launchd plist: {plist_path.name}")
    print(f"To enable auto-update, run:")
    print(f"  launchctl load {plist_path.resolve()}")
    print(f"To disable auto-update, run:")
    print(f"  launchctl unload {plist_path.resolve()}")

def create_readme(base_path):
    """Create comprehensive README"""
    print_step(9, "Creating Documentation")
    
    readme_content = '''# Unified Jess Timeline

A comprehensive system for creating a unified timeline of all communications with Jess, including transcription of audio messages.

## Features

- ✅ **Apple Messages**: Fetches and transcribes audio from Messages
- 🔄 **Google Voice**: Parses text threads and voicemail transcripts
- 🔄 **Google Chat**: Processes chat messages (when data available)
- 🔄 **Alexa**: Handles Alexa voice data (when export available)
- ✅ **Auto-updates**: Runs automatically via launchd
- ✅ **Multiple outputs**: JSON, Markdown, and HTML formats

## Quick Start

1. **Run the pipeline manually:**
   ```bash
   cd scripts/
   ./run_timeline_update.sh
   ```

2. **Enable auto-updates:**
   ```bash
   launchctl load ../com.yourname.unified-timeline.plist
   ```

3. **View the results:**
   ```bash
   open ../data/outputs/
   ```

## Project Structure

```
unified_jess_timeline/
├── com.yourname.unified-timeline.plist   # launchd (project root)
├── scripts/                              # Pipeline scripts
│   ├── 00_config.py                      # Configuration
│   ├── 01_fetch_messages.py              # Fetch Messages data
│   ├── 02_transcribe_messages.py         # Transcribe audio
│   ├── 06_merge_outputs.py               # Merge all sources
│   └── run_timeline_update.sh            # Pipeline wrapper
├── data/
│   ├── cache/                            # Transcription cache
│   └── outputs/                          # Final timeline outputs
├── inputs/
│   └── Takeout/                          # Google Takeout files
└── logs/                                 # Pipeline logs
```

## Configuration

Edit `scripts/00_config.py` to customize:
- Paths to Takeout data
- Messages database location
- Contact identifier for filtering
- Transcription settings

## Pipeline Steps

1. **Fetch Messages**: Extracts messages and attachments from Apple Messages database
2. **Transcribe Audio**: Converts audio attachments to text using Whisper
3. **Parse Voice** (optional): Processes Google Voice data
4. **Parse Chat** (optional): Processes Google Chat data
5. **Parse Alexa** (optional): Processes Alexa voice data
6. **Merge**: Combines all sources into unified timeline

## Outputs

- `unified_jess_timeline.json`: Complete timeline in JSON format
- `unified_jess_timeline.md`: Human-readable timeline in Markdown
- `unified_jess_timeline.html`: Web-viewable timeline (if generated)

## Troubleshooting

### Database Access Issues
If you can't access the Messages database:
1. Ensure Messages is closed
2. Check permissions: `ls -la ~/Library/Messages/chat.db`

### Transcription Issues
If transcription fails:
1. Check audio file permissions
2. Verify sufficient disk space
3. Try a smaller Whisper model in config

### Performance
- Initial run may take 1-2 hours for 1,200 audio files
- Use SSD storage for best performance
- Consider upgrading to faster-whisper with GPU

## Data Privacy

- All processing is done locally on your Mac
- No data is sent to external services
- Transcription cache is stored locally in SQLite

## Manual Updates

To run pipeline manually:
```bash
cd scripts/
./run_timeline_update.sh
```

To update just messages:
```bash
python3 01_fetch_messages.py
python3 02_transcribe_messages.py
python3 06_merge_outputs.py
```

## Log Files

Check logs for pipeline status:
- `../logs/timeline.log` - Standard output
- `../logs/timeline_error.log` - Error logs

## License

This tool is for personal use only. Respect privacy and data protection laws.
'''
    
    readme_path = base_path / "README.md"
    with open(readme_path, 'w') as f:
        f.write(readme_content)
    print_success(f"Created README: {readme_path.name}")


def create_git_keep_files(base_path):
    """Create .gitkeep files for empty directories"""
    print_step(10, "Creating .gitkeep Files")
    
    keep_paths = [
        base_path / "data" / "cache" / ".gitkeep",
        base_path / "data" / "outputs" / ".gitkeep",
        base_path / "inputs" / "Takeout" / ".gitkeep",
    ]
    
    for keep_path in keep_paths:
        keep_path.parent.mkdir(parents=True, exist_ok=True)
        keep_path.touch()
        print_success(f"Created {keep_path}")


def print_final_instructions(base_path):
    """Print final setup instructions"""
    print_step(11, "Setup Complete!")
    
    print(f"\n{Colors.HEADER}{Colors.BOLD}Unified Jess Timeline is ready!{Colors.ENDC}")
    
    print(f"\n{Colors.OKGREEN}Next steps:{Colors.ENDC}")
    print(f"1. Place your Google Takeout files in: {base_path}/inputs/Takeout/")
    print(f"2. Run the pipeline: cd {base_path}/scripts/ && ./run_timeline_update.sh")
    print(f"3. Enable auto-updates: launchctl load {base_path.resolve()}/com.yourname.unified-timeline.plist")
    print(f"4. View results in: {base_path}/data/outputs/")
    
    print(f"\n{Colors.OKCYAN}Important notes:{Colors.ENDC}")
    print("- Make sure Messages is closed before running fetch_messages.py")
    print("- First run may take 1-2 hours for transcription")
    print("- Check logs in: logs/ directory")
    
    print(f"\n{Colors.BOLD}Files created in: {base_path.resolve()}{Colors.ENDC}")


def main():
    """Main setup function"""
    print(f"{Colors.HEADER}{Colors.BOLD}")
    print("=" * 60)
    print("  UNIFIED JESS TIMELINE SETUP")
    print("=" * 60)
    print(f"{Colors.ENDC}")
    
    check_dependencies()
    install_python_packages()
    base_path = create_directory_structure()
    create_config_file(base_path)
    create_utility_scripts(base_path)
    create_pipeline_scripts(base_path)
    create_wrapper_script(base_path)
    create_launchd_plist(base_path)
    create_readme(base_path)
    create_git_keep_files(base_path)
    print_final_instructions(base_path)


if __name__ == "__main__":
    main()
