import streamlit as st
import requests
import base64
import urllib.parse
import html

st.set_page_config(page_title="Social", layout="centered", initial_sidebar_state="collapsed")

# Minimal caption styling: make post captions smaller and slightly muted
st.markdown(
    """
    <style>
    .small-caption { font-size: 12px; color: #555; line-height: 1.2; }
    </style>
    """,
    unsafe_allow_html=True,
)

# Initialize session state
if 'token' not in st.session_state:
    st.session_state.token = None
if 'user' not in st.session_state:
    st.session_state.user = None


def get_headers():
    """Get authorization headers with token"""
    if st.session_state.token:
        return {"Authorization": f"Bearer {st.session_state.token}"}
    return {}


def login_page():
    st.title("Social")
    
    with st.form("auth_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        
        col1, col2 = st.columns(2)
        with col1:
            login = st.form_submit_button("Login", use_container_width=True)
        with col2:
            signup = st.form_submit_button("Sign Up", use_container_width=True)
        
        if login:
            try:
                login_data = {"username": email, "password": password}
                response = requests.post("http://localhost:8000/auth/jwt/login", data=login_data)
                
                if response.status_code == 200:
                    token_data = response.json()
                    st.session_state.token = token_data["access_token"]
                    
                    user_response = requests.get("http://localhost:8000/users/me", headers=get_headers())
                    if user_response.status_code == 200:
                        st.session_state.user = user_response.json()
                        st.rerun()
                else:
                    st.error("Invalid credentials")
            except requests.exceptions.ConnectionError:
                st.error("Cannot connect to server. Start backend: `uvicorn app.app:app --reload`")
        
        if signup:
            try:
                signup_data = {"email": email, "password": password}
                response = requests.post("http://localhost:8000/auth/register", json=signup_data)
                
                if response.status_code == 201:
                    st.success("Account created")
                else:
                    st.error("Registration failed")
            except requests.exceptions.ConnectionError:
                st.error("Cannot connect to server. Start backend: `uvicorn app.app:app --reload`")


def upload_page():
    uploaded_file = st.file_uploader("Choose file", type=['png', 'jpg', 'jpeg', 'mp4', 'avi', 'mov'])
    caption = st.text_input("Caption (optional)")

    if uploaded_file and st.button("Post", use_container_width=True):
        try:
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
            data = {"caption": caption}
            response = requests.post("http://localhost:8000/upload", files=files, data=data, headers=get_headers())

            if response.status_code == 200:
                st.success("Posted")
                st.rerun()
            else:
                st.error("Upload failed")
        except requests.exceptions.ConnectionError:
            st.error("Cannot connect to server")


def encode_text_for_overlay(text):
    """Encode text for ImageKit overlay - base64 then URL encode"""
    if not text:
        return ""
    # Base64 encode the text
    base64_text = base64.b64encode(text.encode('utf-8')).decode('utf-8')
    # URL encode the result
    return urllib.parse.quote(base64_text)


def create_transformed_url(original_url, transformation_params, caption=None):
    if caption:
        encoded_caption = encode_text_for_overlay(caption)
        # Add text overlay at bottom with semi-transparent background
        text_overlay = f"l-text,ie-{encoded_caption},ly-N20,lx-20,fs-100,co-white,bg-000000A0,l-end"
        transformation_params = text_overlay

    if not transformation_params:
        return original_url

    parts = original_url.split("/")

    imagekit_id = parts[3]
    file_path = "/".join(parts[4:])
    base_url = "/".join(parts[:4])
    return f"{base_url}/tr:{transformation_params}/{file_path}"


def feed_page():
    try:
        response = requests.get("http://localhost:8000/feed", headers=get_headers())
        
        if response.status_code != 200:
            st.error("Failed to load feed")
            return
        
        posts = response.json()["posts"]
        
        if not posts:
            st.info("No posts yet")
            return

        for post in posts:
            col1, col2 = st.columns([5, 1])
            
            with col1:
                st.caption(f"{post['email']} · {post['created_at'][:10]}")
            
            with col2:
                if post.get('is_owner', False):
                    if st.button("×", key=f"del_{post['id']}", help="Delete"):
                        try:
                            response = requests.delete(f"http://localhost:8000/post/{post['id']}", headers=get_headers())
                            if response.status_code == 200:
                                st.rerun()
                        except requests.exceptions.ConnectionError:
                            st.error("Cannot connect to server")
            
            if post['file_type'] == 'image':
                uniform_url = create_transformed_url(post['url'], "", post.get('caption', ''))
                st.image(uniform_url, use_container_width=True)
            else:
                uniform_url = create_transformed_url(post['url'], "w-600,h-400,cm-pad_resize")
                st.video(uniform_url)
            
            if post.get('caption'):
                # escape caption content to avoid HTML injection when rendering
                escaped = html.escape(post['caption'])
                st.markdown(f"<div class='small-caption'>{escaped}</div>", unsafe_allow_html=True)
            
            st.divider()
    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to server. Start backend with: `uvicorn app.app:app --reload`")


# Main app logic
if st.session_state.user is None:
    login_page()
else:
    # Top bar with navigation
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("Feed", use_container_width=True):
            st.session_state.page = "feed"
    
    with col2:
        if st.button("Upload", use_container_width=True):
            st.session_state.page = "upload"
    
    with col3:
        if st.button("Logout", use_container_width=True):
            st.session_state.user = None
            st.session_state.token = None
            st.rerun()
    
    st.divider()
    
    # Default page
    if 'page' not in st.session_state:
        st.session_state.page = "feed"
    
    if st.session_state.page == "feed":
        feed_page()
    else:
        upload_page()