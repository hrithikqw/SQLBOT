import streamlit as st
from pathlib import Path
from sqlalchemy import create_engine
from langchain.sql_database import SQLDatabase
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_groq import ChatGroq
from langchain.agents import create_sql_agent
from langchain.agents.agent_types import AgentType
from langchain.callbacks import StreamlitCallbackHandler
import tempfile
import os

# ──────────────────────────────────────────────────────
# 🎨 Page Setup & Custom CSS
st.set_page_config(
    page_title="SQL BOT - AI Database Assistant", 
    page_icon="🤖", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize theme in session state
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False

# Theme toggle functionality - SINGLE BUTTON ONLY
# 🔁 Light/Dark Mode Toggle — minimal moon/sun icon only
toggle_icon = '🌙' if not st.session_state.dark_mode else '☀️'
toggle_col = st.columns([11, 1])[1]
with toggle_col:
    if st.button(toggle_icon, help="Toggle Theme", key="theme_toggle_icon"):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()


# Define theme colors based on current mode
def get_theme_colors():
    if st.session_state.dark_mode:
        return {
            'bg': '#0e1117',
            'text': '#fafafa',
            'secondary_bg': '#262730',
            'border': '#464853',
            'card_bg': '#1e1e2e',
            'gradient_start': '#667eea',
            'gradient_end': '#764ba2',
            'success_bg': '#1a472a',
            'success_color': '#4ade80',
            'success_border': '#22543d',
            'error_bg': '#5b1d1d',
            'error_color': '#ef4444',
            'error_border': '#7f1d1d',
            'feature_bg': 'rgba(102, 126, 234, 0.2)',
            'main_content_bg': 'rgba(102, 126, 234, 0.15)',
            'main_content_border': 'rgba(102, 126, 234, 0.3)'
        }
    else:
        return {
            'bg': '#ffffff',
            'text': '#262626',
            'secondary_bg': '#f8fafc',
            'border': '#e2e8f0',
            'card_bg': '#f1f5f9',
            'gradient_start': '#667eea',
            'gradient_end': '#764ba2',
            'success_bg': '#dcfce7',
            'success_color': '#15803d',
            'success_border': '#bbf7d0',
            'error_bg': '#fef2f2',
            'error_color': '#dc2626',
            'error_border': '#fecaca',
            'feature_bg': 'rgba(102, 126, 234, 0.1)',
            'main_content_bg': 'rgba(102, 126, 234, 0.08)',
            'main_content_border': 'rgba(102, 126, 234, 0.2)'
        }
colors = get_theme_colors()

# Custom CSS with proper theme support
st.markdown(f"""
<style>
    /* Main app background */
    .stApp {{
        background-color: {colors['bg']} !important;
        color: {colors['text']} !important;
    }}
    
    /* Sidebar styling */
    .css-1d391kg, .css-1cypcdb, section[data-testid="stSidebar"] {{
        background-color: {colors['secondary_bg']} !important;
    }}
    
    /* Text elements */
    .stMarkdown, .stText, p, span, div {{
        color: {colors['text']} !important;
    }}
    
    /* Reduce top padding */
    .block-container {{
        padding-top: 1rem;
        padding-bottom: 0rem;
    }}
    
    /* Main title styling */
    .main-title {{
        background: linear-gradient(90deg, {colors['gradient_start']} 0%, {colors['gradient_end']} 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 0.5rem;
        margin-top: 0;
    }}
    
    /* Sidebar SQLBOT title */
    .sidebar-header {{
        background: linear-gradient(45deg, {colors['gradient_start']}, {colors['gradient_end']});
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        text-align: center;
    }}
    
    .sidebar-header h1 {{
        color: white !important;
        font-size: 1.8rem;
        margin: 0;
        font-weight: bold;
    }}
    
    .sidebar-header p {{
        color: rgba(255, 255, 255, 0.8) !important;
        margin: 0.3rem 0 0 0;
        font-size: 0.85rem;
    }}
    
    /* Connection status indicator */
    .connection-status {{
        padding: 0.75rem;
        border-radius: 8px;
        text-align: center;
        margin: 1rem 0;
        font-weight: bold;
        border: 1px solid;
    }}
    
    .connected {{
        background-color: {colors['success_bg']};
        color: {colors['success_color']} !important;
        border-color: {colors['success_border']};
    }}
    
    .disconnected {{
        background-color: {colors['error_bg']};
        color: {colors['error_color']} !important;
        border-color: {colors['error_border']};
    }}
    
    /* Database info card */
    .db-info {{
        background: {colors['card_bg']};
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid {colors['gradient_start']};
        color: {colors['text']} !important;
    }}
    
    /* Feature highlights */
    .feature-box {{
        background: {colors['feature_bg']};
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 3px solid {colors['gradient_start']};
        color: {colors['text']} !important;
    }}
    
    /* File upload info */
    .file-upload-info {{
        background: {colors['feature_bg']};
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        border-left: 3px solid {colors['gradient_start']};
        color: {colors['text']} !important;
    }}
    
    /* Main content styling */
    .main-content-box {{
        text-align: center;
        padding: 1.5rem;
        background: {colors['main_content_bg']};
        border-radius: 10px;
        margin-bottom: 1.5rem;
        border: 1px solid {colors['main_content_border']};
    }}
    
    .main-content-box h3 {{
        color: {colors['gradient_start']} !important;
        margin-bottom: 0.5rem;
    }}
    
    .main-content-box p {{
        color: {colors['text']} !important;
        opacity: 0.8;
        margin: 0;
    }}
    
    /* Custom button styling */
    .stButton > button {{
        background: linear-gradient(45deg, {colors['gradient_start']}, {colors['gradient_end']}) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.5rem 1rem !important;
        font-weight: bold !important;
        transition: all 0.3s ease !important;
    }}
    
    .stButton > button:hover {{
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2) !important;
    }}
    
    /* Theme toggle button specific styling */
    button[title="Toggle Dark/Light Mode"] {{
        width: 35px !important;
        height: 35px !important;
        min-height: 35px !important;
        padding: 0 !important;
        font-size: 18px !important;
        border-radius: 6px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }}
    
    /* Chat message styling */
    .stChatMessage {{
        background-color: {colors['card_bg']} !important;
        border-radius: 10px !important;
        margin-bottom: 1rem !important;
        color: {colors['text']} !important;
    }}
    
    /* Input fields */
    .stTextInput > div > div > input {{
        background-color: {colors['secondary_bg']} !important;
        color: {colors['text']} !important;
        border-color: {colors['border']} !important;
    }}
    
    .stSelectbox > div > div > select {{
        background-color: {colors['secondary_bg']} !important;
        color: {colors['text']} !important;
        border-color: {colors['border']} !important;
    }}
    
    /* Radio buttons */
    .stRadio > div {{
        color: {colors['text']} !important;
    }}
    
    /* Expander */
    .streamlit-expanderHeader {{
        background-color: {colors['secondary_bg']} !important;
        color: {colors['text']} !important;
    }}
    
    .streamlit-expanderContent {{
        background-color: {colors['card_bg']} !important;
        color: {colors['text']} !important;
    }}
    
    /* Success/Error messages */
    .stSuccess {{
        background-color: {colors['success_bg']} !important;
        color: {colors['success_color']} !important;
    }}
    
    .stError {{
        background-color: {colors['error_bg']} !important;
        color: {colors['error_color']} !important;
    }}
    
    .stWarning {{
        background-color: {colors['feature_bg']} !important;
        color: {colors['text']} !important;
    }}
    
    .stInfo {{
        background-color: {colors['feature_bg']} !important;
        color: {colors['text']} !important;
    }}
    
    /* Footer styling */
    .footer-text {{
        text-align: center;
        color: {colors['text']} !important;
        opacity: 0.7;
        padding: 1rem;
    }}
    
    /* Hide Streamlit branding */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────
# 🤖 Sidebar - SQLBOT Branding
with st.sidebar:
    st.markdown(f"""
    <div class="sidebar-header">
        <h1>🤖 SQL BOT</h1>
        <p>AI-Powered Database Assistant</p>
    </div>
    """, unsafe_allow_html=True)

# ──────────────────────────────────────────────────────
# 🧠 Database Connection Mode
LOCAL_DB = 'USE_LOCALDB'
MYSQL = 'USE_MYSQL'
UPLOAD_DB = 'USE_UPLOADED'
radio_opt = ['🗃️ Use SQLite Database', '📁 Upload Database File', '🌐 Connect to MySQL']

with st.sidebar:
    st.markdown("### 🔗 Database Connection")
    selected_opt = st.radio("Choose your database type:", radio_opt, label_visibility="collapsed")

# Initialize session state for uploaded file
if 'uploaded_file' not in st.session_state:
    st.session_state.uploaded_file = None
if 'temp_db_path' not in st.session_state:
    st.session_state.temp_db_path = None

# ──────────────────────────────────────────────────────
# 🛠️ Database Configuration
with st.sidebar.expander("⚙️ Database Settings", expanded=True):
    if radio_opt.index(selected_opt) == 2:  # MySQL option
        db_uri = MYSQL
        mysql_host = st.text_input('🌐 Host Name', placeholder="localhost")
        mysql_user = st.text_input('👤 Username', placeholder="root")
        mysql_pass = st.text_input('🔐 Password', type='password')
        mysql_db = st.text_input('🗄️ Database Name', placeholder="my_database")
    elif radio_opt.index(selected_opt) == 1:  # Upload option
        db_uri = UPLOAD_DB
        st.markdown("### 📤 Upload Your Database")
        
        uploaded_db = st.file_uploader(
            "Choose your SQLite database file",
            type=['db', 'sqlite', 'sqlite3'],
            help="Upload a SQLite database file (.db, .sqlite, .sqlite3)",
            key="db_uploader"
        )
        
        # Store uploaded file in session state
        if uploaded_db is not None:
            st.session_state.uploaded_file = uploaded_db
            st.success(f"✅ File uploaded: {uploaded_db.name}")
            st.info(f"📊 File size: {uploaded_db.size / 1024:.1f} KB")
        elif st.session_state.uploaded_file is not None:
            st.success(f"✅ Using previously uploaded file: {st.session_state.uploaded_file.name}")
        else:
            st.markdown("""
            <div class="file-upload-info">
                <strong>📁 Supported file types:</strong><br>
                • .db files<br>
                • .sqlite files<br>
                • .sqlite3 files<br><br>
                <em>Click "Browse files" above to select your database file</em>
            </div>
            """, unsafe_allow_html=True)
    else:  # Default SQLite option
        db_uri = LOCAL_DB
        st.info("📁 Using local Chinook.db SQLite database")

# ──────────────────────────────────────────────────────
# 🔑 API Configuration
with st.sidebar:
    st.markdown("### 🔑 API Configuration")
    api_key = st.text_input('Groq API Key', type='password', placeholder="Enter your Groq API key...")
    
    if api_key:
        st.markdown('<div class="connection-status connected">✅ API Key Configured</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="connection-status disconnected">❌ API Key Required</div>', unsafe_allow_html=True)

# ──────────────────────────────────────────────────────
# 🧹 Chat Controls
with st.sidebar:
    st.markdown("### 🎛️ Chat Controls")
    clear_btn = st.button('🧹 Clear Chat History', use_container_width=True)
    
    # Feature highlights
    st.markdown("### ✨ Features")
    st.markdown("""
    <div class="feature-box">
        <strong>🔍 Smart Query Detection</strong><br>
        Automatically detects SQL vs general queries
    </div>
    <div class="feature-box">
        <strong>📊 Multi-Database Support</strong><br>
        SQLite, MySQL, and file upload support
    </div>
    <div class="feature-box">
        <strong>📁 File Upload</strong><br>
        Upload your own SQLite database files
    </div>
    <div class="feature-box">
        <strong>💬 Natural Language</strong><br>
        Ask questions in plain English
    </div>
    """, unsafe_allow_html=True)

# ──────────────────────────────────────────────────────
# 🏠 Main Page Header
st.markdown('<h1 class="main-title">💬 Chat with Your SQL Database</h1>', unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown(f"""
    <div class="main-content-box">
        <h3>🚀 Ask anything about your database!</h3>
        <p>Natural language queries • SQL generation • File upload support • Data insights</p>
    </div>
    """, unsafe_allow_html=True)

# ──────────────────────────────────────────────────────
# ⚠️ API Key Check
if not api_key:
    st.error("🔑 Please enter your Groq API Key in the sidebar to continue.")
    st.info("💡 Get your free API key from [Groq Console](https://console.groq.com/)")
    st.stop()

# ──────────────────────────────────────────────────────
# 🤖 Initialize LLM
llm = ChatGroq(groq_api_key=api_key, model_name='Llama3-8b-8192', streaming=True)

def cleanup_temp_files():
    """Clean up temporary database files"""
    if st.session_state.temp_db_path and os.path.exists(st.session_state.temp_db_path):
        try:
            os.unlink(st.session_state.temp_db_path)
            st.session_state.temp_db_path = None
        except:
            pass

def configure_db(db_uri, mysql_host=None, mysql_user=None, mysql_pass=None, mysql_db=None, uploaded_file=None):
    if db_uri == LOCAL_DB:
        dbfilepath = (Path(__file__).parent / 'Chinook.db').absolute()
        if not dbfilepath.exists():
            raise FileNotFoundError("Chinook.db not found. Please ensure the database file exists in the same directory.")
        return SQLDatabase(create_engine(f'sqlite:///{dbfilepath}'))
    
    elif db_uri == MYSQL:
        if not (mysql_host and mysql_user and mysql_pass and mysql_db):
            raise ValueError("Please complete all MySQL connection details.")
        return SQLDatabase(create_engine(f'mysql+mysqlconnector://{mysql_user}:{mysql_pass}@{mysql_host}/{mysql_db}'))
    
    elif db_uri == UPLOAD_DB:
        if uploaded_file is None:
            raise ValueError("Please upload a database file to continue.")
        
        # Clean up previous temp files
        cleanup_temp_files()
        
        # Create a new temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_file_path = tmp_file.name
        
        try:
            # Test the database connection
            engine = create_engine(f'sqlite:///{tmp_file_path}')
            db = SQLDatabase(engine)
            
            # Verify it's a valid SQLite database by trying to get tables
            tables = db.get_usable_table_names()
            if not tables:
                raise ValueError("The uploaded file appears to be empty or invalid.")
            
            # Store the temp file path in session state
            st.session_state.temp_db_path = tmp_file_path
            
            return db
        except Exception as e:
            # Clean up on error
            if os.path.exists(tmp_file_path):
                os.unlink(tmp_file_path)
            raise e

# ──────────────────────────────────────────────────────
# 💾 Database Connection
try:
    if db_uri == MYSQL:
        db = configure_db(db_uri, mysql_host, mysql_user, mysql_pass, mysql_db)
        st.success(f"✅ Connected to MySQL database: {mysql_db}")
    elif db_uri == UPLOAD_DB:
        # Use the uploaded file from session state if available
        current_file = uploaded_db if uploaded_db is not None else st.session_state.uploaded_file
        
        if current_file is not None:
            db = configure_db(db_uri, uploaded_file=current_file)
            st.success(f"✅ Connected to uploaded database: {current_file.name}")
        else:
            st.warning("⚠️ Please upload a database file to continue.")
            st.stop()
    else:
        db = configure_db(db_uri)
        st.success("✅ Connected to local SQLite database (Chinook.db)")
    
    # Database info
    with st.expander("📊 Database Information", expanded=False):
        db_type = "MySQL" if db_uri == MYSQL else "SQLite (Uploaded)" if db_uri == UPLOAD_DB else "SQLite (Default)"
        if db_uri == MYSQL:
            db_name = mysql_db
        elif db_uri == UPLOAD_DB:
            current_file = uploaded_db if uploaded_db is not None else st.session_state.uploaded_file
            db_name = current_file.name if current_file else "Unknown"
        else:
            db_name = "Chinook.db"
        
        try:
            table_names = db.get_usable_table_names()
            st.markdown(f"""
            <div class="db-info">
                <strong>Database Type:</strong> {db_type}<br>
                <strong>Database Name:</strong> {db_name}<br>
                <strong>Tables Available:</strong> {len(table_names)}<br>
                <strong>Connection Status:</strong> <span style="color: {colors['success_color']};">✅ Active</span>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("🔍 Show Table Names"):
                st.write("**Available Tables:**")
                for table in table_names:
                    st.write(f"• {table}")
        except Exception as e:
            st.error(f"❌ Error getting database information: {e}")

except Exception as e:
    st.error(f"❌ Database connection failed: {e}")
    if db_uri == UPLOAD_DB:
        st.error("💡 Make sure your uploaded file is a valid SQLite database (.db, .sqlite, .sqlite3)")
    elif db_uri == LOCAL_DB:
        st.error("💡 Make sure Chinook.db exists in the same directory as this script")
    st.stop()

# ──────────────────────────────────────────────────────
# 🤖 Create SQL Agent
try:
    toolkit = SQLDatabaseToolkit(db=db, llm=llm)
    agent = create_sql_agent(
        llm=llm,
        toolkit=toolkit,
        handle_parsing_errors=True,
        verbose=False,
        agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION
    )
except Exception as e:
    st.error(f"❌ Failed to create SQL agent: {e}")
    st.stop()

# ──────────────────────────────────────────────────────
# 💬 Chat Interface
if 'messages' not in st.session_state or clear_btn:
    st.session_state['messages'] = [
        {
            'role': 'assistant', 
            'content': '👋 Hello! I\'m SQLBOT, your AI database assistant. Ask me anything about your database - I can help you write queries, analyze data, or just chat!'
        }
    ]

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg['role']):
        st.write(msg['content'])

# ──────────────────────────────────────────────────────
# ⌨️ Chat Input
user_query = st.chat_input("💭 Ask about your data, request a query, or just say hi...", key="chat_input")

if user_query:
    # Add user message
    st.session_state.messages.append({'role': 'user', 'content': user_query})
    with st.chat_message('user'):
        st.write(user_query)

    # Generate response
    with st.chat_message('assistant'):
        streamlit_callback = StreamlitCallbackHandler(st.container())
        
        try:
            # 🔍 Smart query detection
            sql_keywords = ['select', 'from', 'table', 'column', 'data', 'where', 'join', 'count', 'sum', 'avg', 'group by', 'order by']
            is_sql_related = any(keyword in user_query.lower() for keyword in sql_keywords)
            
            with st.spinner('🤖 SQLBOT is thinking...'):
                if is_sql_related:
                    response = agent.run(user_query, callbacks=[streamlit_callback])
                else:
                    response = llm.invoke(user_query)
                
                # Clean response text
                clean_text = str(response) if isinstance(response, str) else response.content
                
                # Add assistant response to history
                st.session_state.messages.append({'role': 'assistant', 'content': clean_text})
                st.write(clean_text)

        except Exception as e:
            error_msg = f"❌ Oops! Something went wrong: {str(e)}"
            st.error(error_msg)
            st.session_state.messages.append({'role': 'assistant', 'content': error_msg})

# ──────────────────────────────────────────────────────
# 🧹 Cleanup on app termination
import atexit
atexit.register(cleanup_temp_files)

# ──────────────────────────────────────────────────────
