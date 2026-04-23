"""
Terminal UI for DeepSeek
"""
import os
from backend import DeepSeekClient, DEFAULT_SYSTEM_PROMPT

# ANSI color codes
GREEN = "\033[92m"
BLUE = "\033[94m"
YELLOW = "\033[93m"
RED = "\033[91m"
CYAN = "\033[96m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"
CLEAR_LINE = "\033[2K\r"

# ========== INITIALIZE ==========
client = DeepSeekClient()

# ========== DISPLAY HEADER ==========
print()
print(f"{BOLD}{CYAN}╔════════════════════════════════════════════════════╗{RESET}")
print(f"{BOLD}{CYAN}║     🤖 DEEPSEEK CHAT - EXTENSIVE MODE 🤖          ║{RESET}")
print(f"{BOLD}{CYAN}╚════════════════════════════════════════════════════╝{RESET}")
print()
print(f"{YELLOW}📋 System Prompt Active:{RESET}")
print(f"{DIM}  {client.system_prompt.strip().split(chr(10))[0]}...{RESET}")
print()
print(f"{GREEN}💡 Commands:{RESET}")
print(f"   {BLUE}quit{RESET}  - Exit chat")
print(f"   {BLUE}new{RESET}   - Start fresh conversation")
print(f"   {BLUE}system{RESET} - Change system prompt")
print(f"   {BLUE}clear{RESET} - Clear screen")
print()
print(f"{DIM}{'─' * 50}{RESET}")

# ========== MAIN LOOP ==========
while True:
    # Get user input
    user_input = input(f"\n{BOLD}{BLUE}┌─[{BOLD}{GREEN}You{BOLD}{BLUE}]{RESET}\n└─▶ {RESET}").strip()
    
    if user_input.lower() == 'quit':
        print(f"\n{YELLOW}👋 Goodbye! Stay strong.{RESET}\n")
        break
    
    elif user_input.lower() == 'new':
        client.reset_conversation()
        print(f"\n{GREEN}✨ Started new conversation!{RESET}\n")
        continue
    
    elif user_input.lower() == 'system':
        print(f"{YELLOW}📝 Current prompt: {client.system_prompt[:100]}...{RESET}")
        new_prompt = input(f"{CYAN}Enter new system prompt: {RESET}").strip()
        if new_prompt:
            client.set_system_prompt(new_prompt)
            print(f"{GREEN}✅ System prompt updated!{RESET}")
        continue
    
    elif user_input.lower() == 'clear':
        os.system('cls' if os.name == 'nt' else 'clear')
        continue
    
    elif not user_input:
        continue
    
    # Show thinking animation
    print(f"{DIM}🤔 Thinking...{RESET}", end="", flush=True)
    
    # Get response
    reply, tokens, cost = client.send_message(user_input)
    
    # Clear thinking line and display response
    print(CLEAR_LINE, end="", flush=True)
    print(f"\n{BOLD}{GREEN}┌─[{BOLD}{CYAN}DeepSeek{BOLD}{GREEN}]{RESET}")
    print(f"{BOLD}{GREEN}└─▶{RESET} ")
    print(f"{reply}")
    print(f"{DIM}[⚡ Tokens: {tokens} | 💰 Cost: ${cost:.6f}]{RESET}")
    print()