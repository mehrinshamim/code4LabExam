# Code4LabExam

An AI powered tool that'll help you prepare for your Lab Exams - currently incorporated only for S4 Operating Systems Lab.

## What it does

- Generates detailed documentation for OS lab programs
- Provides proper output formats required in lab exams
- Creates downloadable PDFs for exam preparation
- Analyzes and explains C code implementations

## Generated Documentation Includes

- **Overview**: Core OS concept explanation
- **Algorithm**: Both short and detailed steps
- **Code**: Complete C implementation with comments
- **Explanation**: Detailed logic and implementation details


## How to Use

1. Enter your OS lab question (e.g., "Implement FCFS scheduling")
2. (Optional) Add your C code if you have an implementation
3. Click "Generate Documentation"
4. Select sections to include in PDF
5. Download and use for exam preparation!


## Tech Stack

- **Frontend**: React + Vite, TailwindCSS
- **Backend**: FastAPI, Python
- **AI**: Google Gemini
- **Documentation**: PDF Generation

## Running Locally

Requirements:

- Node.js v14+
- Python 3.8+
- Google Gemini API key

1. **Clone & Install**

```bash
git clone https://github.com/yourusername/code4LabExam.git
cd code4LabExam
```

2. **Set up Backend**

```bash
cd server
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# Create .env file with your Gemini API key
echo GEMINI_API_KEY=your_key_here > .env
```

3. **Set up Frontend**

```bash
cd client
npm install
```

4. **Run the Application**

```bash
# Terminal 1: Start Backend
cd server
venv\Scripts\activate
uvicorn main:app --reload

# Terminal 2: Start Frontend
cd client
npm run dev
```

5. Open `http://localhost:5173` in your browser


## License

MIT License - See [LICENSE](LICENSE.txt) file

---

⭐ Star this repo if it helped with your OS Lab exam preparation!
