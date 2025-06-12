# 🤖 SQLBOT – Chat with Your Database

SQLBOT is an AI-powered database assistant built with Streamlit, LangChain, and Groq.  
It lets you **chat naturally** with your **SQLite or MySQL database**, ask questions like  
"List all customers from Canada" or just say "Hi" – and it replies smartly.

---

## 🧠 Description

SQLBOT is designed for:
- Data analysts or devs who want to explore DBs quickly
- Non-technical users who want to query data without SQL
- Teams looking to embed an AI SQL layer in their apps

Core features:
- 🔍 Natural language to SQL query conversion  
- 🧠 General chat + database assistant in one  
- 🌗 Dark/Light mode toggle  
- 🗃 Drag and drop support for `.sql`, `.sqlite`, and `.db` files (SQLite databases)  
- 🌐 MySQL connection support via credentials  
- 📊 Table name listing, smart SQL fallback, and intent detection  

---

## 🛠️ Tech Stack

| Tech            | Description                                      |
|-----------------|--------------------------------------------------|
| **Streamlit**   | Frontend for UI and chat interface               |
| **LangChain**   | Agent framework to connect LLMs with databases   |
| **Groq API**    | Lightning-fast LLM inference for natural queries |
| **SQLAlchemy**  | Manages SQL database connections                 |
| **SQLite/MySQL**| Database support                                 |

---


## 🚀 Installation


- **Clone this repo (or fork and then clone):**
  ```bash
  git clone https://github.com/your-username/sqlbot.git
  cd sqlbot
 
- **Install dependencies:**
  ```bash
  pip install -r requirements txt
- **After installing, create a .env file and add your Groq API key:**
  ```bash
  GROQ_API_KEY = 'ENTER_YOUR_GROQ_API'
  
- **Run the app:**
  ```bash
  streamlit run app.py

- **Use the app:**
     Upload your `.db`, `.sqlite`, or `.sql` file, or connect to MySQL from the sidebar

### 🎉 You're now ready to chat with your database using SQLBOT!
---



## 💡 Final Notes

If you found this project helpful or inspiring, feel free to ⭐ star the repo or fork it to build your own version.

For questions, suggestions, or contributions — open an issue or PR. I'd love to collaborate!

---

