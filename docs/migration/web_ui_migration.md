u# Web UI Migration Plan for MAYA

## Overview
This document outlines the steps to transition MAYA's UI from PyQt6 to a modern web-based frontend while maintaining the existing Python backend. This will allow for more flexible UI design using standard web technologies (HTML/CSS/JavaScript) while leveraging Python's powerful backend capabilities.

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│  Web Frontend   │ ◄───┤  WebSocket     ├────►│  Python        │
│  (HTML/CSS/JS)  │     │  Server        │     │  Backend       │
│                 │     │  (Tornado)     │     │  (Existing     │
└─────────────────┘     └─────────────────┘     │  Logic)        │
                                               └─────────────────┘
```

## Migration Steps

### 1. Set Up Web Server

#### 1.1 Add Required Dependencies
Add to `requirements.txt`:
```
tornado>=6.1
python-socketio>=5.0.0
flask-socketio>=5.0.0
python-engineio>=4.0.0
```

#### 1.2 Create Web Server
Create `web_server.py`:
```python
import tornado.web
import tornado.websocket
import tornado.ioloop
import json
import asyncio
from modules.voice import VoiceAssistant
from modules.character import CharacterSystem

class WebSocketHandler(tornado.websocket.WebSocketHandler):
    def initialize(self, voice_assistant, character_system):
        self.voice_assistant = voice_assistant
        self.character_system = character_system

    async def on_message(self, message):
        data = json.loads(message)
        if data['type'] == 'user_message':
            # Process message using existing backend
            response = await self.process_message(data['content'])
            self.write_message(json.dumps({
                'type': 'bot_response',
                'content': response
            }))

    async def process_message(self, message):
        # Integrate with existing message processing
        return "Response to: " + message

def make_app():
    voice = VoiceAssistant()
    character = CharacterSystem()
    
    return tornado.web.Application([
        (r'/ws', WebSocketHandler, {
            'voice_assistant': voice,
            'character_system': character
        }),
        (r'/(.*)', tornado.web.StaticFileHandler, {
            'path': 'web/static',
            'default_filename': 'index.html'
        }),
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
```

### 2. Frontend Development

#### 2.1 Directory Structure
```
web/
├── static/
│   ├── css/
│   │   └── styles.css
│   ├── js/
│   │   └── app.js
│   ├── assets/
│   │   └── (images, fonts, etc.)
│   └── index.html
└── templates/
    └── (server-side templates if needed)
```

#### 2.2 Example index.html
```html
<!DOCTYPE html>
<html>
<head>
    <title>MAYA Web UI</title>
    <link rel="stylesheet" href="/static/css/styles.css">
</head>
<body>
    <div id="app">
        <div id="chat-container">
            <div id="messages"></div>
            <div class="input-area">
                <input type="text" id="message-input" placeholder="Type a message...">
                <button id="send-button">Send</button>
                <button id="voice-button">🎤</button>
            </div>
        </div>
    </div>
    <script src="/static/js/app.js"></script>
</body>
</html>
```

#### 2.3 Example app.js
```javascript
class MAYAWebUI {
    constructor() {
        this.socket = new WebSocket('ws://localhost:8888/ws');
        this.setupEventListeners();
    }

    setupEventListeners() {
        document.getElementById('send-button').addEventListener('click', () => this.sendMessage());
        document.getElementById('message-input').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.sendMessage();
        });
        
        this.socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (data.type === 'bot_response') {
                this.displayMessage('maya', data.content);
            }
        };
    }

    sendMessage() {
        const input = document.getElementById('message-input');
        const message = input.value.trim();
        
        if (message) {
            this.displayMessage('user', message);
            this.socket.send(JSON.stringify({
                type: 'user_message',
                content: message
            }));
            input.value = '';
        }
    }

    displayMessage(sender, content) {
        const messagesDiv = document.getElementById('messages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;
        messageDiv.textContent = content;
        messagesDiv.appendChild(messageDiv);
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }
}

// Initialize the application
window.onload = () => {
    window.mayaUI = new MAYAWebUI();
};
```

### 3. Integration with Existing Backend

#### 3.1 Message Processing
Modify the WebSocket handler to use existing message processing:
```python
async def process_message(self, message):
    # Example integration with existing message processing
    response = await self.character_system.generate_response(
        message,
        voice_enabled=self.voice_assistant.is_voice_enabled()
    )
    
    if self.voice_assistant.is_voice_enabled():
        await self.voice_assistant.speak(response)
        
    return response
```

#### 3.2 Voice Integration
Add WebSocket handlers for voice commands:
```python
class VoiceHandler(tornado.websocket.WebSocketHandler):
    def initialize(self, voice_assistant):
        self.voice_assistant = voice_assistant
        self.listening = False

    async def open(self):
        print("Voice WebSocket opened")

    async def on_message(self, message):
        data = json.loads(message)
        if data['type'] == 'start_listening':
            self.start_listening()
        elif data['type'] == 'audio_data':
            await self.process_audio(data['audio'])

    def start_listening(self):
        self.listening = True
        # Initialize voice recognition

    async def process_audio(self, audio_data):
        # Process audio and convert to text
        try:
            text = await self.voice_assistant.recognize(audio_data)
            if text:
                self.write_message(json.dumps({
                    'type': 'transcription',
                    'text': text
                }))
        except Exception as e:
            print(f"Error processing audio: {e}")
```

### 4. Development Workflow

#### 4.1 Local Development
1. Start the web server:
   ```bash
   python web_server.py
   ```
2. Open `http://localhost:8888` in a web browser
3. Use a tool like `webpack` or `vite` for frontend development with hot-reload

#### 4.2 Building for Production
1. Bundle frontend assets:
   ```bash
   npm run build  # Or your preferred build tool
   ```
2. Serve static files through the Python server

### 5. UI Customization

#### 5.1 Styling
Edit `web/static/css/styles.css` to customize the look and feel:
```css
:root {
    --primary-color: #4a6fa5;
    --background-color: #f5f7fa;
    --text-color: #333;
}

body {
    font-family: 'Segoe UI', system-ui, sans-serif;
    margin: 0;
    padding: 0;
    background-color: var(--background-color);
    color: var(--text-color);
}

#chat-container {
    max-width: 800px;
    margin: 0 auto;
    padding: 20px;
    height: 100vh;
    display: flex;
    flex-direction: column;
}

#messages {
    flex-grow: 1;
    overflow-y: auto;
    padding: 10px;
}

.message {
    margin: 10px 0;
    padding: 10px 15px;
    border-radius: 18px;
    max-width: 70%;
}

.message.user {
    background-color: var(--primary-color);
    color: white;
    margin-left: auto;
}

.message.maya {
    background-color: #e9ecef;
    margin-right: auto;
}

.input-area {
    display: flex;
    padding: 10px 0;
    gap: 10px;
}

#message-input {
    flex-grow: 1;
    padding: 10px 15px;
    border: 1px solid #ddd;
    border-radius: 20px;
    font-size: 16px;
}

button {
    background-color: var(--primary-color);
    color: white;
    border: none;
    border-radius: 20px;
    padding: 10px 20px;
    cursor: pointer;
    font-size: 16px;
}

button:hover {
    opacity: 0.9;
}
```

### 6. Deployment

#### 6.1 Docker Configuration
Update `Dockerfile` to include Node.js and build the frontend:
```dockerfile
# Build frontend
FROM node:16 as frontend-builder
WORKDIR /app/web
COPY web/package*.json ./
RUN npm install
COPY web/ .
RUN npm run build

# Python backend
FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    portaudio19-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy frontend build
COPY --from=frontend-builder /app/web/dist /app/web/static

# Copy and install Python dependencies
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt

# Run the application
CMD ["python", "web_server.py"]
```

#### 6.2 docker-compose.yml
```yaml
version: '3.8'
services:
  maya:
    build: .
    ports:
      - "8888:8888"
    volumes:
      - ./web/static:/app/web/static
      - maya-data:/app/data
    environment:
      - PYTHONUNBUFFERED=1
    restart: unless-stopped

volumes:
  maya-data:
```

## Migration Checklist

### Phase 1: Setup (1-2 days)
- [ ] Set up web server with WebSocket
- [ ] Create basic HTML/CSS/JS structure
- [ ] Implement basic message passing

### Phase 2: Core Features (3-5 days)
- [ ] Integrate with existing message processing
- [ ] Implement voice input/output
- [ ] Add character animations

### Phase 3: UI/UX (3-7 days)
- [ ] Design responsive layout
- [ ] Add loading states
- [ ] Implement error handling
- [ ] Add accessibility features

### Phase 4: Testing & Optimization (2-3 days)
- [ ] Cross-browser testing
- [ ] Performance optimization
- [ ] Security review

## Next Steps
1. Set up the basic web server structure
2. Create a simple UI prototype
3. Gradually migrate functionality from PyQt6 to web
4. Test each component as it's migrated

## Notes
- The existing Python backend logic can be largely reused
- WebSockets provide real-time communication
- The web UI can be styled independently of the backend
- Consider using a frontend framework (React, Vue, etc.) for more complex UIs
