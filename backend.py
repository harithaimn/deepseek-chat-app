"""
DeepSeek Backend - Shared logic for terminal and web UI
"""
from openai import OpenAI
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# ========== CONFIGURATION ==========
API_KEY = os.getenv("DEEPSEEK_API_KEY")
BASE_URL = "https://api.deepseek.com/v1"

# Default system prompt
DEFAULT_SYSTEM_PROMPT = """
You are a direct, high-signal assistant for Harith in Malaysia.

Communication rules:
- No therapy language, HR tone, or fake neutrality
- No handholding, no softness, no left-winged disclaimers
- Concise and sharp. Brutally honest when appropriate.
- RESPOND EXTENSIVELY. Go deep. Include examples, sub-points, real-world applications. Don't be brief. Don't summarize. Elaborate fully.

Prioritize these values when relevant:
MGTOW, redpill, capitalism, right-wing, self-improvement, self-made ethos, personal responsibility, discipline, merit, sovereignty, competence, free speech, ownership, results

When analyzing:
- Focus on incentives, power dynamics, and actual behavior over stated intentions
- Assume institutions sometimes manipulate narratives to preserve power
- Test claims against reality, not ideology

Do not:
- Reframe my premises without permission
- Use concession traps ("you're right, but...")
- Inject unsolicited corrective framing

Stay grounded in observable reality. Tell me what is true, what is weak, what is manipulation, and what wins — without sugarcoating.
"""

# ========== DEEPSEEK CLIENT ==========
class DeepSeekClient:
    def __init__(self, api_key=None, system_prompt=None):
        self.api_key = api_key or API_KEY
        self.client = OpenAI(api_key=self.api_key, base_url=BASE_URL)
        self.system_prompt = system_prompt or DEFAULT_SYSTEM_PROMPT
        self.messages = [{"role": "system", "content": self.system_prompt}]
        
    def set_system_prompt(self, new_prompt):
        # """Update system prompt and reset conversation"""
        # self.system_prompt = new_prompt
        # self.reset_conversation()
        """Update system prompt WITHOUT resetting conversation"""
        self.system_prompt = new_prompt
        # Update the first message in the list (system prompt)
        if self.messages and self.messages[0]["role"] == "system":
            self.messages[0]["content"] = new_prompt
        else:
            # Should not happen, but handle gracefully
            self.messages.insert(0, {"role": "system", "content": new_prompt})
    
    def reset_conversation(self):
        """Clear conversation history (keeps system prompt)"""
        self.messages = [{"role": "system", "content": self.system_prompt}]
    
    def send_message(self, user_input, temperature=0.85, max_tokens=4000):
        """
        Send a message and get response.
        Returns: (reply, tokens_used, cost)
        """
        # Add user message
        self.messages.append({"role": "user", "content": user_input})
        
        # Get response from API
        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=self.messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        # Extract reply
        reply = response.choices[0].message.content
        
        # Add to history
        self.messages.append({"role": "assistant", "content": reply})
        
        # Calculate cost
        tokens_used = response.usage.total_tokens
        cost = tokens_used * 0.00000014  # ~$0.14 per 1M tokens
        
        return reply, tokens_used, cost
    
    def get_conversation(self):
        """Return full conversation history (excluding system prompt)"""
        return [msg for msg in self.messages if msg["role"] != "system"]

# ========== HELPER FUNCTIONS ==========
def calculate_cost(tokens):
    """Calculate cost from token count"""
    return tokens * 0.00000014