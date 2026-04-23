"""
Chat Manager - Handles saving, loading, and managing chat conversations
"""
import json
import os
from datetime import datetime
from pathlib import Path

# Storage directory
CHATS_DIR = Path("chats")
CHATS_DIR.mkdir(exist_ok=True)

class ChatManager:
    def __init__(self):
        self.current_chat_id = None
        self.load_all_chats()
    
    def load_all_chats(self):
        """Load all saved chats from JSON files"""
        self.chats = {}
        for file in CHATS_DIR.glob("*.json"):
            with open(file, 'r') as f:
                chat_data = json.load(f)
                self.chats[chat_data['id']] = chat_data
        return self.chats
    
    def create_new_chat(self, title="New Chat"):
        """Create a new chat with unique ID"""
        chat_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        new_chat = {
            "id": chat_id,
            "title": title,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "messages": []
        }
        self.chats[chat_id] = new_chat
        self.current_chat_id = chat_id
        self._save_chat(chat_id)
        return chat_id
    
    def save_current_chat(self, messages, system_prompt=None):
        """Save current conversation to JSON"""
        if not self.current_chat_id:
            self.create_new_chat()
        
        chat = self.chats[self.current_chat_id]
        
        # Auto-generate title from first user message if still "New Chat"
        if chat["title"] == "New Chat" and messages:
            first_user_msg = next((m["content"] for m in messages if m["role"] == "user"), None)
            if first_user_msg:
                # Use first 50 chars as title
                chat["title"] = first_user_msg[:50] + ("..." if len(first_user_msg) > 50 else "")
        
        chat["messages"] = messages
        chat["updated_at"] = datetime.now().isoformat()
        if system_prompt:
            chat["system_prompt"] = system_prompt
        
        self._save_chat(self.current_chat_id)
    
    def _save_chat(self, chat_id):
        """Save individual chat to JSON file"""
        filepath = CHATS_DIR / f"{chat_id}.json"
        with open(filepath, 'w') as f:
            json.dump(self.chats[chat_id], f, indent=2)
    
    def load_chat(self, chat_id):
        """Load a specific chat by ID"""
        if chat_id in self.chats:
            self.current_chat_id = chat_id
            return self.chats[chat_id]
        return None
    
    def delete_chat(self, chat_id):
        """Delete a chat"""
        if chat_id in self.chats:
            filepath = CHATS_DIR / f"{chat_id}.json"
            if filepath.exists():
                filepath.unlink()
            del self.chats[chat_id]
            if self.current_chat_id == chat_id:
                self.current_chat_id = None
            return True
        return False
    
    def rename_chat(self, chat_id, new_title):
        """Rename a chat"""
        if chat_id in self.chats:
            self.chats[chat_id]["title"] = new_title
            self._save_chat(chat_id)
            return True
        return False
    
    def get_chat_list(self):
        """Get list of all chats for sidebar"""
        chat_list = []
        for chat_id, chat in self.chats.items():
            chat_list.append({
                "id": chat_id,
                "title": chat["title"],
                "created_at": chat["created_at"],
                "updated_at": chat["updated_at"]
            })
        # Sort by updated_at descending (most recent first)
        chat_list.sort(key=lambda x: x["updated_at"], reverse=True)
        return chat_list