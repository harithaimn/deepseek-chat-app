"""
Streamlit Dashboard for DeepSeek
"""
import streamlit as st
from backend import DeepSeekClient, DEFAULT_SYSTEM_PROMPT
from s3_chat_manager import S3ChatManager

# ========== PAGE CONFIG ==========
st.set_page_config(
    page_title="DeepSeek Chat",
    page_icon="🤖",
    layout="wide"
)

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

# ========== LOAD CHAT FROM URL ON STARTUP ==========
chat_id_from_url = st.query_params.get("chat_id")

if chat_id_from_url:
    chat_data = st.session_state.chat_manager.load_chat(chat_id_from_url)
    if chat_data:
        st.session_state.current_messages = chat_data.get("messages", [])
        st.session_state.chat_manager.current_chat_id = chat_id_from_url
        
        # Get system prompt from saved chat or keep current
        sys_prompt = chat_data.get("system_prompt", st.session_state.client.system_prompt)
        
        # Rebuild client.messages with full conversation history
        st.session_state.client.messages = [{"role": "system", "content": sys_prompt}]
        for msg in st.session_state.current_messages:
            st.session_state.client.messages.append(msg)
        
        # Update client's system prompt
        st.session_state.client.system_prompt = sys_prompt
    else:
        st.session_state.current_messages = []
else:
    st.session_state.current_messages = []

# ========== SIDEBAR ==========
with st.sidebar:
    st.title("💬 Chats")
    
    # New Chat button
    if st.button("➕ New Chat", use_container_width=True):
        new_id = st.session_state.chat_manager.create_new_chat()
        st.session_state.current_messages = []
        st.session_state.client.reset_conversation()
        st.query_params.clear()
        st.rerun()
    
    st.markdown("### Recent Chats")
    
    # Display all chats
    for chat in st.session_state.chat_manager.get_chat_list():
        col1, col2, col3 = st.columns([4, 0.5, 0.5])
        with col1:
            if st.button(f"💬 {chat['title'][:30]}", key=f"chat_{chat['id']}", use_container_width=True):
                chat_data = st.session_state.chat_manager.load_chat(chat['id'])
                if chat_data:
                    st.session_state.current_messages = chat_data.get("messages", [])
                    
                    # Get system prompt from saved chat
                    sys_prompt = chat_data.get("system_prompt", st.session_state.client.system_prompt)
                    
                    # Rebuild client.messages with full conversation history
                    st.session_state.client.messages = [{"role": "system", "content": sys_prompt}]
                    for msg in st.session_state.current_messages:
                        st.session_state.client.messages.append(msg)
                    
                    # Update client's system prompt
                    st.session_state.client.system_prompt = sys_prompt
                    
                    st.query_params["chat_id"] = chat['id']
                    st.rerun()
        with col2:
            if st.button("✏️", key=f"rename_{chat['id']}", help="Rename"):
                st.session_state.rename_chat_id = chat['id']
                st.rerun()
        with col3:
            if st.button("🗑️", key=f"delete_{chat['id']}", help="Delete"):
                st.session_state.chat_manager.delete_chat(chat['id'])
                if st.session_state.chat_manager.current_chat_id == chat['id']:
                    st.session_state.current_messages = []
                    st.session_state.chat_manager.current_chat_id = None
                    st.session_state.client.reset_conversation()
                st.rerun()
    
    # Rename dialog
    if "rename_chat_id" in st.session_state:
        new_title = st.text_input("New title:", value="")
        if st.button("Save", key="save_rename"):
            if new_title:
                st.session_state.chat_manager.rename_chat(st.session_state.rename_chat_id, new_title)
                del st.session_state.rename_chat_id
                st.rerun()
    
    st.divider()
    
    # Settings
    with st.expander("⚙️ Settings"):
        temperature = st.slider("Temperature", 0.0, 1.5, 0.7, 0.05)
        max_tokens = st.slider("Max Tokens", 500, 8000, 4000, 500)
        
        # System prompt editor
        system_prompt = st.text_area(
            "System Prompt",
            value=st.session_state.client.system_prompt,
            height=300
        )
        
        if st.button("Apply System Prompt", key="apply_system_prompt"):
            # Update without resetting conversation
            st.session_state.client.system_prompt = system_prompt
            if st.session_state.client.messages and st.session_state.client.messages[0]["role"] == "system":
                st.session_state.client.messages[0]["content"] = system_prompt
            else:
                st.session_state.client.messages.insert(0, {"role": "system", "content": system_prompt})
            
            # Save to current chat
            st.session_state.chat_manager.save_current_chat(
                st.session_state.current_messages,
                system_prompt
            )
            st.rerun()
    
    # Stats
    st.markdown("### 📊 Stats")
    if "total_tokens" in st.session_state:
        st.metric("Total Tokens", st.session_state.total_tokens)
    if "total_cost" in st.session_state:
        st.metric("Total Cost", f"${st.session_state.total_cost:.6f}")

# ========== MAIN CHAT INTERFACE ==========
st.title("🤖 DeepSeek Chat")

# Show current chat title
current_title = st.session_state.chat_manager.chats.get(
    st.session_state.chat_manager.current_chat_id, {}
).get("title", "New Chat")
st.caption(f"📌 Current chat: {current_title} | 🌡️ Temperature: {temperature} | 📝 Max Tokens: {max_tokens}")

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

                # RIGHT HERE - add this line:
                st.query_params["chat_id"] = st.session_state.chat_manager.current_chat_id
                
            except Exception as e:
                st.error(f"Error: {e}")
    
    st.rerun()