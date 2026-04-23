"""
S3 Chat Manager - Stores chats in AWS S3 instead of local files
"""
import json
import boto3
from datetime import datetime
from io import BytesIO

class S3ChatManager:
    def __init__(self, bucket_name, prefix="trp-data/chats"):
        self.bucket_name = bucket_name
        self.prefix = prefix
        self.s3 = boto3.client('s3')
        self.current_chat_id = None
        self.chats = {}
        self.load_all_chats()
    
    def load_all_chats(self):
        """Load all chats from S3"""
        self.chats = {}
        try:
            # List all JSON files in the bucket
            response = self.s3.list_objects_v2(
                Bucket=self.bucket_name, 
                Prefix=f"{self.prefix}/"
            )
            
            if 'Contents' in response:
                for obj in response['Contents']:
                    key = obj['Key']
                    if key.endswith('.json'):
                        # Get the file content
                        file_obj = self.s3.get_object(Bucket=self.bucket_name, Key=key)
                        chat_data = json.loads(file_obj['Body'].read().decode('utf-8'))
                        self.chats[chat_data['id']] = chat_data
        except Exception as e:
            print(f"Error loading chats from S3: {e}")
        return self.chats
    
    def create_new_chat(self, title="New Chat"):
        """Create a new chat"""
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
        """Save current chat to S3"""
        if not self.current_chat_id:
            self.create_new_chat()
        
        chat = self.chats[self.current_chat_id]
        
        # Auto-generate title
        if chat["title"] == "New Chat" and messages:
            first_user_msg = next((m["content"] for m in messages if m["role"] == "user"), None)
            if first_user_msg:
                chat["title"] = first_user_msg[:50] + ("..." if len(first_user_msg) > 50 else "")
        
        chat["messages"] = messages
        chat["updated_at"] = datetime.now().isoformat()
        if system_prompt:
            chat["system_prompt"] = system_prompt
        
        self._save_chat(self.current_chat_id)
    
    def _save_chat(self, chat_id):
        """Save individual chat to S3"""
        key = f"{self.prefix}/{chat_id}.json"
        json_str = json.dumps(self.chats[chat_id], indent=2)
        self.s3.put_object(Bucket=self.bucket_name, Key=key, Body=json_str.encode('utf-8'))
    
    def load_chat(self, chat_id):
        """Load a specific chat"""
        if chat_id in self.chats:
            self.current_chat_id = chat_id
            return self.chats[chat_id]
        return None
    
    def delete_chat(self, chat_id):
        """Delete a chat from S3"""
        if chat_id in self.chats:
            key = f"{self.prefix}/{chat_id}.json"
            self.s3.delete_object(Bucket=self.bucket_name, Key=key)
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
        """Get list of all chats"""
        chat_list = []
        for chat_id, chat in self.chats.items():
            chat_list.append({
                "id": chat_id,
                "title": chat["title"],
                "created_at": chat["created_at"],
                "updated_at": chat["updated_at"]
            })
        chat_list.sort(key=lambda x: x["updated_at"], reverse=True)
        return chat_list