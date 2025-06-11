# Pokémon MCP Server 🎮⚡
app link: https://pokemonmcpserver.streamlit.app/
demolink: https://drive.google.com/file/d/1kA3IO0a1GzDYc20y3DSLGLCvIBvvqKUY/view?usp=sharing

A modular AI-powered middleware server for Pokémon data retrieval, team building, and strategic analysis.

## ✨ Features

- **🔍 Pokémon Search**: Detailed information retrieval from PokeAPI
- **⚖️ Pokémon Comparison**: Side-by-side stat and attribute analysis
- **🤖 AI Team Builder**: Generate balanced teams from natural language descriptions
- **🎯 Strategic Counters**: AI-powered counter-Pokémon suggestions
- **🌐 Web Interface**: Interactive Streamlit frontend
- **📊 Comprehensive Logging**: Full request tracking and error monitoring

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Google Gemini API Key

### Installation

1. **Clone & Setup**
```bash
git clone <your-repo-url>
cd pokemon-mcp-server
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install Dependencies**
```bash
pip install fastapi uvicorn requests python-dotenv langchain-google-genai langchain-core streamlit
```

3. **Environment Configuration**
```bash
# Create .env file
echo "GEMINI_API_KEY=your_api_key_here" > .env
```

4. **Run the Application**
```bash
# Start backend (Terminal 1)
uvicorn main:app --reload

# Start frontend (Terminal 2)
streamlit run streamlit_app.py
```

5. **Access the Application**
- **API Documentation**: http://localhost:8000/docs
- **Web Interface**: http://localhost:8501

## 🛠️ API Endpoints


| `/pokemon/{name}` | GET | Get detailed Pokémon information |
| `/compare/{pokemon1}/{pokemon2}` | GET | Compare two Pokémon |
| `/team/generate` | POST | Generate team from description |
| `/counters/{pokemon_name}` | GET | Get counter suggestions |

## 📋 Example Usage

### Get Pokémon Data
```bash
curl http://localhost:8000/pokemon/pikachu
```

### Generate Team
```bash
curl -X POST http://localhost:8000/team/generate \
  -H "Content-Type: application/json" \
  -d '{"description": "balanced team with strong defense"}'
```

## 🏗️ Architecture

```
Web Frontend (Streamlit) ←→ MCP Server (FastAPI) ←→ PokeAPI
                                    ↓
                            Google Gemini AI
```

### Modular Components
- **Information Retrieval**: PokeAPI data fetching and normalization
- **Comparison Module**: Multi-Pokémon analysis
- **Strategy Module**: AI-powered counter suggestions
- **Team Composition**: Natural language team generation

```

## 🚢 Deployment

### Docker
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Variables
```env
GEMINI_API_KEY=your_gemini_api_key
ENVIRONMENT=production
LOG_LEVEL=INFO
```

## 📁 Project Structure

```
pokemon-mcp-server/
├── main.py              # FastAPI backend
├── streamlit_app.py     # Web interface
├── .env                 # Environment variables
├── requirements.txt     # Dependencies
├── tests/              # Test files
└── docs/               # Documentation
```

## 🔧 Tech Stack

- **Backend**: FastAPI, Python
- **AI**: Google Gemini (LangChain)
- **Frontend**: Streamlit
- **External API**: PokeAPI
- **Environment**: python-dotenv

## 📝 License

MIT License - see LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📞 Support

For issues and questions:
- Create an issue on GitHub
- Check the [full documentation](docs/README.md)

---

**Built with ❤️ for Pokémon trainers and AI enthusiasts**

