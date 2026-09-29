# 🎓 AI Study Assistant

![Node.js](https://img.shields.io/badge/Node.js-339933?style=for-the-badge&logo=nodedotjs&logoColor=white)
![Express.js](https://img.shields.io/badge/Express.js-404D59?style=for-the-badge)
![Gemini AI](https://img.shields.io/badge/Google%20Gemini-8E75B2?style=for-the-badge&logo=google&logoColor=white)
![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)

An intelligent, purpose-driven educational utility application built to enhance student learning through Active Recall, automated summarization, and guided feedback. Powered by the Google Gemini LLM API.

---

## 📖 Problem Statement
Many existing AI tools function as generic "chatbots" that provide immediate answers to student queries. While convenient, this promotes **passive reading**—a state where students experience the "illusion of competence" by reading an answer without actually retrieving the information from their own memory. There is a need for a dedicated utility that forces students to engage with their material actively, providing structural feedback rather than just doing the work for them.

## 🎯 Objective
To build a functional, beginner-friendly AI-powered student utility that moves beyond simple chat interfaces. The goal is to facilitate **Active Recall** and **Study Material Transformation** by implementing an interactive feedback loop, all while utilizing strict prompt engineering, robust error handling, and a clean user interface.

## 🚀 Proposed Methodology (How the App Works)
The application is designed as a structured Single-Page Application (SPA) offering four specific tools. Users can paste text or upload files (PDF, DOCX, TXT, MD, Images), which are parsed on the backend and sent to the Google Gemini API using highly constrained system prompts.

1. **ELI5 & Summarizer:** Distills dense academic text into a 3-bullet summary and a real-world analogy.
2. **Active Recall Quiz:** A two-step process. First, it generates a question from the notes. Second, it waits for the student's attempt before evaluating it.
3. **Draft Polisher:** Reviews a draft response and provides 2-3 constructive suggestions without rewriting the text.
4. **Ask a Tutor:** Allows students to ask targeted questions and receive clear, structured explanations.

## 📂 Folder Structure
```text
📦 Utility App
 ┣ 📂 public
 ┃ ┣ 📜 index.html       # The main Single-Page Application UI
 ┃ ┣ 📜 app.js           # Frontend logic, state management, and API calls
 ┃ ┗ 📜 style.css        # Custom CSS styles (alongside Tailwind)
 ┣ 📜 server.js          # Node.js/Express backend & Gemini API integration
 ┣ 📜 package.json       # Project metadata and dependencies
 ┣ 📜 .env               # Environment variables (API Keys)
 ┗ 📜 README.md          # Project documentation
```

## 🛠️ Prompt Structure Used
To make the outputs reliable, the application uses **strict system prompts** in the backend so the user never has to worry about prompt engineering. 

* **Active Recall Quiz:** The prompt explicitly instructs the AI: *"Generate ONE short-answer question... DO NOT provide the answer. ONLY provide the question."* This prevents the model from proactively answering its own question.
* **Draft Polisher:** The prompt is constrained with: *"Do NOT rewrite the text entirely. Instead, provide 2-3 specific, constructive suggestions."* This ensures the AI acts as a strict tutor rather than doing the homework for the student.
* **Evaluation Phase:** The model is forced to output a structured evaluation starting with a bold verdict (*"**Verdict: Correct/Incorrect**"*).

## 🛡️ Error Handling
To prevent wasting API tokens and ensure a smooth user experience, both frontend and backend validation are implemented:
* **Frontend Validation:** The UI blocks empty submissions and enforces minimum character limits (e.g., 50 characters for generating a quiz).
* **Backend Validation:** The server strictly verifies file types during uploads and validates text lengths.
* **Graceful Failure:** If the API times out, hits rate limits, or fails, the backend catches the error in a `try/catch` block. Instead of crashing the app, it sends a polite, user-friendly error message to the frontend, which is displayed in a dedicated status bar. Buttons also utilize loading spinners and are disabled during API calls to prevent double-submissions.

## 💡 AI-Assisted Workflow vs. Generic Chatbot
This application proves its utility by prioritizing **workflow over open-ended chat**. 

If this were a generic chatbot, a student might ask for a quiz and immediately receive both the questions and the answers. This application forces a **two-step Active Recall workflow**: the AI generates the question, hides the state, waits for the student to actively type an attempt, and *then* grades it. This creates a genuine, interactive feedback loop that actually improves memory retention, proving it is a purpose-driven utility rather than just an isolated prompt call.

---

## ⚙️ Setup & Installation (From Scratch)

If you are running this on a completely fresh machine, follow these steps:

### 1. Install Node.js (Required)
The application requires Node.js to run the backend server.
1. Download Node.js from the official website: [https://nodejs.org/](https://nodejs.org/) (Choose the **LTS** version).
2. Run the installer. **Keep all default settings** (Ensure "Add to PATH" is checked).
3. Open a **new** Terminal or Command Prompt.

### 2. Clone the Repository
Download or clone this project to your local machine:
```bash
git clone <your-repository-url-here>
cd "Utility App"
```

### 3. Set Up API Keys
This app uses the Google Gemini API.
1. Get a free API key from [Google AI Studio](https://aistudio.google.com/).
2. In the root directory of the project, create a file named exactly `.env`.
3. Add the following line to the file, replacing the placeholder with your actual key:
```env
GEMINI_API_KEY=your_actual_api_key_here
```

### 4. Install Dependencies
Run the following command in your terminal to install all required packages (Express, Multer, Gemini SDK, etc.):
```bash
npm install
```

## 🖥️ Running the Application

1. Start the backend server:
```bash
node server.js
```
*You should see a message saying `Server is running on http://localhost:3000`.*

2. Open your preferred web browser and navigate to:
**http://localhost:3000**

## 📊 Results
The resulting application is a fast, responsive, and intuitive web tool. File text extraction works seamlessly across multiple formats (PDF, DOCX, Images). The LLM prompt engineering successfully constraints the AI to specific educational personas, ensuring that quizzes do not leak answers and draft reviews do not completely rewrite the user's input. The state management handles the two-step quiz flow flawlessly.

## 🏁 Conclusion
The AI Study Assistant successfully demonstrates how to transform a generic Large Language Model into a highly specialized educational utility. By focusing on prompt engineering, UI state management, and the pedagogical concept of Active Recall, the project bridges the gap between raw AI capabilities and practical, real-world user needs.
