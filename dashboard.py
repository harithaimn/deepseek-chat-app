"""
Streamlit Dashboard for DeepSeek
"""
import streamlit as st
from backend import DeepSeekClient, DEFAULT_SYSTEM_PROMPT
#from chat_manager import ChatManager
from s3_chat_manager import S3ChatManager

# ========== PAGE CONFIG ==========
st.set_page_config(
    page_title="DeepSeek Chat",
    page_icon="🤖",
    layout="wide"
)


# ========== PASSWORD PROTECTION ==========
def check_password():
    """Returns True if user is logged in"""
    if st.session_state.get("authenticated", False):
        return True
    
    password = st.text_input("Enter password to access:", type="password")
    if st.button("Login"):
        if password == st.secrets["PASSWORD"]:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Wrong password")
    return False

if not check_password():
    st.stop()

    

# ========== INITIALIZE SESSION ==========
if "client" not in st.session_state:
    st.session_state.client = DeepSeekClient()
    
if "chat_manager" not in st.session_state:
    st.session_state.chat_manager = S3ChatManager(bucket_name=st.secrets["S3_BUCKET_NAME"])

    
if "current_messages" not in st.session_state:
    st.session_state.current_messages = []
    
if "total_tokens" not in st.session_state:
    st.session_state.total_tokens = 0
    st.session_state.total_cost = 0.0

# Don't load any chat on startup - just show empty state
if st.session_state.chat_manager.current_chat_id is None:
    st.session_state.current_messages = []
    # Don't create or load any chat
else:
    # Load existing chat messages
    current_chat = st.session_state.chat_manager.load_chat(st.session_state.chat_manager.current_chat_id)
    if current_chat and "messages" in current_chat:
        st.session_state.current_messages = current_chat["messages"]
        # Load system prompt if saved
        if "system_prompt" in current_chat:
            st.session_state.client.set_system_prompt(current_chat["system_prompt"])


# ========== SIDEBAR ==========
with st.sidebar:
    st.title("💬 Chats")
    
    # # New Chat button
    # if st.button("➕ New Chat", use_container_width=True):
    #     new_id = st.session_state.chat_manager.create_new_chat()
    #     st.session_state.current_messages = []
    #     st.session_state.client.reset_conversation()
    #     st.rerun()
    
    # st.divider()
    
    # Display all chats with inline actions
    st.markdown("### Recent Chats")

    # New Chat button at top
    if st.button("➕ New Chat", use_container_width=True):
        new_id = st.session_state.chat_manager.create_new_chat()
        st.session_state.current_messages = []
        st.session_state.client.reset_conversation()
        st.rerun()

    #st.divider()

    for chat in st.session_state.chat_manager.get_chat_list():
        col1, col2, col3 = st.columns([4, 0.5, 0.5])
        with col1:
            if st.button(f"💬 {chat['title'][:30]}", key=f"chat_{chat['id']}", use_container_width=True):
                chat_data = st.session_state.chat_manager.load_chat(chat['id'])
                if chat_data:
                    st.session_state.current_messages = chat_data.get("messages", [])
                    if "system_prompt" in chat_data:
                        st.session_state.client.set_system_prompt(chat_data["system_prompt"])
                    st.rerun()
        with col2:
            if st.button("✏️", key=f"rename_{chat['id']}", help="Rename"):
                st.session_state.rename_chat_id = chat['id']
                st.rerun()
        with col3:
            if st.button("🗑️", key=f"delete_{chat['id']}", help="Delete"):
                # Delete this chat
                st.session_state.chat_manager.delete_chat(chat['id'])
                # If this was the current chat, clear it
                if st.session_state.chat_manager.current_chat_id == chat['id']:
                    st.session_state.current_messages = []
                    st.session_state.chat_manager.current_chat_id = None
                    st.session_state.client.reset_conversation()
                st.rerun()

    # Rename dialog (keep this as is)
    if "rename_chat_id" in st.session_state:
        new_title = st.text_input("New title:", value="")
        #if st.button("Save"):
        if st.button("Save", key="save_rename"):
            if new_title:
                st.session_state.chat_manager.rename_chat(st.session_state.rename_chat_id, new_title)
                del st.session_state.rename_chat_id
                st.rerun()

    
    st.divider()
    
    # Settings
    with st.expander("⚙️ Settings"):
        temperature = st.slider("Temperature", 0.0, 1.5, 0.7, 0.05)
        max_tokens = st.slider("Max Tokens", 500, 4000, 4000, 500)
        
        # System prompt editor
        system_prompt = st.text_area(
            "System Prompt",
            value=st.session_state.client.system_prompt,
            height=300
        )
        
        #if st.button("Apply System Prompt"):
        if st.button("Apply System Prompt", key="apply_system_prompt"):
            st.session_state.client.set_system_prompt(system_prompt)
            # Save to current chat
            st.session_state.chat_manager.save_current_chat(
                st.session_state.current_messages,
                system_prompt
            )
            st.rerun()
    
    # Stats
    #st.divider()
    st.markdown("### 📊 Stats")
    if "total_tokens" in st.session_state:
        st.metric("Total Tokens", st.session_state.total_tokens)
    if "total_cost" in st.session_state:
        st.metric("Total Cost", f"${st.session_state.total_cost:.6f}")


# ========== MAIN CHAT INTERFACE ==========
st.title("🤖 DeepSeek Chat")

# Show current chat title with edit option
current_title = st.session_state.chat_manager.chats.get(
    st.session_state.chat_manager.current_chat_id, {}
).get("title", "New Chat")
st.caption(f"📌 Current chat: {current_title} | 🌡️ Temperature: {temperature} | 📝 Max Tokens: {max_tokens}")

if st.session_state.get("show_rename"):
    new_title = st.text_input("New chat name:", value=current_title)
    #if st.button("Save Name"):
    if st.button("Save Name", key="save_name"):
        if new_title:
            st.session_state.chat_manager.rename_chat(
                st.session_state.chat_manager.current_chat_id,
                new_title
            )
            st.session_state.show_rename = False
            st.rerun()

#st.caption(f"")
#st.divider()

# Display chat history
for msg in st.session_state.current_messages:
    if msg["role"] == "user":
        with st.chat_message("user", avatar="🧑"):
            st.markdown(msg["content"])
    else:
        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(msg["content"], unsafe_allow_html=True)
            if "tokens" in msg:
                st.caption(f"⚡ {msg['tokens']} tokens | 💰 ${msg['cost']:.6f}")


# ========== CHAT INPUT ==========
user_input = st.chat_input("Type your message...")

if user_input:
    # Add user message
    st.session_state.current_messages.append({"role": "user", "content": user_input})
    
    # Get response
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("💭 Thinking..."):
            try:
                reply, tokens, cost = st.session_state.client.send_message(
                    user_input,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                
                st.markdown(reply, unsafe_allow_html=True)
                st.caption(f"⚡ {tokens} tokens | 💰 ${cost:.6f}")
                
                # Add assistant message
                st.session_state.current_messages.append({
                    "role": "assistant",
                    "content": reply,
                    "tokens": tokens,
                    "cost": cost
                })
                
                # Update stats
                st.session_state.total_tokens += tokens
                st.session_state.total_cost += cost
                
                # Save chat automatically
                st.session_state.chat_manager.save_current_chat(
                    st.session_state.current_messages,
                    st.session_state.client.system_prompt
                )
                
            except Exception as e:
                st.error(f"Error: {e}")
    
    st.rerun()