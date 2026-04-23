# 🤖 DeepSeek Chat

Terminal + Web UI for DeepSeek API. Direct, high-signal, no fluff.

## 🚀 Quick Start

```bash
# 1. Clone
git clone https://github.com/yourusername/deepseek-chat-app.git
cd deepseek-chat-app

# 2. Install
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. Add API key
echo "DEEPSEEK_API_KEY=sk-your-key" > .env

# 4. Run
python terminal_ui.py        # Terminal version
streamlit run dashboard.py   # Web version
📁 Project Structure
text
├── backend.py        # Core logic
├── terminal_ui.py    # Terminal app
├── dashboard.py      # Web app
├── chat_manager.py   # Chat storage
├── chats/            # Saved conversations
├── .streamlit/
│   └── config.toml   # Streamlit config
└── .env              # API key
🎮 Commands (Terminal)
Command	Action
quit	Exit
new	New conversation
system	Change system prompt
clear	Clear screen
💬 Chat Features
Persistent storage - Chats saved automatically

Chat history - Browse and resume past conversations

Auto-title - First message becomes chat name

Rename/Delete - Manage your chats

System prompts - Custom AI behavior per chat

⚙️ Configuration
Edit backend.py to change:

System prompt

Model (deepseek-chat or deepseek-reasoner)

Temperature

Max tokens

Or use web dashboard sidebar for live tuning.

💰 Cost
Model	Price
DeepSeek-V3	$0.14/1M tokens
DeepSeek-R1	$0.55/1M tokens
$2 lasts 1-3 months of regular use.

🚢 Deployment Options
Option 1: Streamlit Cloud (Easiest)
Push code to GitHub

Go to share.streamlit.io

Connect your repo

Add secret: DEEPSEEK_API_KEY

Deploy → Public URL

Option 2: Local + ngrok (Free)
bash
streamlit run dashboard.py
# In another terminal
ngrok http 8501
# Get public URL
Option 3: Render.com
Push to GitHub

Create new Web Service on Render

Build command: pip install -r requirements.txt

Start command: streamlit run dashboard.py --server.port $PORT --server.address 0.0.0.0

Add environment variable: DEEPSEEK_API_KEY

Option 4: Fly.io
bash
fly launch
fly secrets set DEEPSEEK_API_KEY=sk-your-key
fly deploy
🔧 Troubleshooting
Issue	Fix
API key not found	Check .env format (no spaces around =)
Port in use	--server.port 8502
Chats not saving	Create chats/ folder
Long text cut off	Increase max_tokens in sidebar
📝 License
MIT