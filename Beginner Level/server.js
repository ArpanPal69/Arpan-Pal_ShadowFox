const express = require('express');
const cors = require('cors');
const dotenv = require('dotenv');
const path = require('path');
const multer = require('multer');
const pdfParse = require('pdf-parse');
const mammoth = require('mammoth');
const Tesseract = require('tesseract.js');
const { GoogleGenerativeAI } = require('@google/generative-ai');

dotenv.config();

const app = express();
const port = process.env.PORT || 3000;

app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// Initialize Google Generative AI
if (!process.env.GEMINI_API_KEY) {
    console.warn("WARNING: GEMINI_API_KEY is not set in the environment.");
}

const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY || "dummy_key");
const model = genAI.getGenerativeModel({ model: "gemini-3.5-flash" });

// File upload setup (Memory Storage, limit to 10MB)
const upload = multer({ storage: multer.memoryStorage(), limits: { fileSize: 10 * 1024 * 1024 } });

app.post('/api/extract-text', upload.single('file'), async (req, res) => {
    try {
        if (!req.file) {
            return res.status(400).json({ error: "No file uploaded." });
        }

        const buffer = req.file.buffer;
        const mimeType = req.file.mimetype;
        const originalName = req.file.originalname.toLowerCase();

        let extractedText = "";

        if (mimeType === 'application/pdf' || originalName.endsWith('.pdf')) {
            const data = await pdfParse(buffer);
            extractedText = data.text;
        } else if (mimeType === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' || originalName.endsWith('.docx')) {
            const result = await mammoth.extractRawText({ buffer: buffer });
            extractedText = result.value;
        } else if (mimeType.startsWith('text/') || originalName.endsWith('.md') || originalName.endsWith('.txt')) {
            extractedText = buffer.toString('utf-8');
        } else if (mimeType.startsWith('image/') || originalName.endsWith('.jpg') || originalName.endsWith('.png') || originalName.endsWith('.jpeg')) {
            const result = await Tesseract.recognize(buffer, 'eng');
            extractedText = result.data.text;
        } else {
            return res.status(400).json({ error: "Unsupported file type. Please upload PDF, DOCX, TXT, MD, or Images (JPG/PNG)." });
        }

        res.json({ text: extractedText.trim() });
    } catch (error) {
        console.error("Text Extraction Error:", error);
        res.status(500).json({ error: `Failed to extract text from the file: ${error.message}` });
    }
});

app.post('/api/summarize', async (req, res) => {
    try {
        const { text } = req.body;
        if (!text || text.length < 20) {
            return res.status(400).json({ error: "Text must be at least 20 characters." });
        }

        const prompt = `You are an expert tutor. Your goal is to help a student understand the provided text. 
First, provide a 3-bullet summary of the most critical points under a '## Summary' header. 
Second, provide a 'Simplified Explanation' using a relatable real-world analogy to explain the core concept to a beginner under a '## ELI5 Explanation' header.

Text to summarize:
${text}`;

        const result = await model.generateContent(prompt);
        res.json({ result: result.response.text() });
    } catch (error) {
        console.error("Summarize API Error:", error);
        res.status(500).json({ error: "The AI encountered an error processing your request. Please try again." });
    }
});

app.post('/api/quiz/generate', async (req, res) => {
    try {
        const { text } = req.body;
        if (!text || text.length < 50) {
            return res.status(400).json({ error: "Please provide more notes to generate a valid quiz (at least 50 characters)." });
        }

        const prompt = `You are a teacher. Read the following notes. Generate ONE short-answer question that tests a crucial concept from these notes. DO NOT provide the answer. ONLY provide the question.

Notes:
${text}`;

        const result = await model.generateContent(prompt);
        res.json({ question: result.response.text().trim() });
    } catch (error) {
        console.error("Quiz Generate API Error:", error);
        res.status(500).json({ error: "Failed to generate quiz. Please try again." });
    }
});

app.post('/api/quiz/evaluate', async (req, res) => {
    try {
        const { material, question, answer } = req.body;
        if (!answer || answer.trim() === '') {
            return res.status(400).json({ error: "Please attempt an answer before submitting." });
        }

        const prompt = `You are a teacher grading a student.
Context (Original Notes): ${material}
Question Asked: ${question}
Student Answer: ${answer}

Evaluate the student's answer. Start with a clear verdict in bold (e.g., '**Verdict: Correct**', '**Verdict: Partially Correct**', '**Verdict: Incorrect**'). 
Then, briefly explain why based on the context notes, and provide the ideal answer.`;

        const result = await model.generateContent(prompt);
        res.json({ evaluation: result.response.text() });
    } catch (error) {
        console.error("Quiz Evaluate API Error:", error);
        res.status(500).json({ error: "Failed to evaluate answer. Please try again." });
    }
});

app.post('/api/polish', async (req, res) => {
    try {
        const { text } = req.body;
        if (!text || text.length < 20) {
            return res.status(400).json({ error: "Text must be at least 20 characters." });
        }

        const prompt = `You are an academic writing coach. Review the provided draft text. 
Do NOT rewrite the text entirely. Instead, provide 2-3 specific, constructive suggestions on how to improve its clarity, academic tone, or structure. 
Conclude with a single paragraph showing a slightly polished version of their work as an example.

Draft text:
${text}`;

        const result = await model.generateContent(prompt);
        res.json({ result: result.response.text() });
    } catch (error) {
        console.error("Polish API Error:", error);
        res.status(500).json({ error: "Failed to polish draft. Please try again." });
    }
});

app.post('/api/ask', async (req, res) => {
    try {
        const { question } = req.body;
        if (!question || question.length < 10) {
            return res.status(400).json({ error: "Please ask a detailed question (at least 10 characters)." });
        }

        const prompt = `You are an expert, encouraging tutor. A student has asked you the following question: 
"${question}"

Please provide a clear, accurate, and easy-to-understand answer. 
Structure your response using headers or bullet points to make it readable. If applicable, use a simple analogy to explain complex concepts.`;

        const result = await model.generateContent(prompt);
        res.json({ result: result.response.text() });
    } catch (error) {
        console.error("Ask API Error:", error);
        res.status(500).json({ error: "Failed to get an answer. Please try again." });
    }
});

app.listen(port, () => {
    console.log(`Server is running on http://localhost:${port}`);
});
