// Global State
let currentQuizQuestion = "";
let originalStudyMaterial = "";

// UI Elements
const statusMessage = document.getElementById('status-message');

function renderContent(element, markdownText) {
    element.innerHTML = marked.parse(markdownText);
    if (window.renderMathInElement) {
        renderMathInElement(element, {
            delimiters: [
                {left: '$$', right: '$$', display: true},
                {left: '$', right: '$', display: false},
                {left: '\\(', right: '\\)', display: false},
                {left: '\\[', right: '\\]', display: true}
            ],
            throwOnError: false
        });
    }
}

function switchMode(mode) {
    // Hide all sections
    document.querySelectorAll('.tool-section').forEach(el => el.classList.add('hidden'));
    
    // Reset all tabs
    document.querySelectorAll('.tab-btn').forEach(el => {
        el.classList.remove('bg-blue-600', 'text-white');
        el.classList.add('bg-gray-200', 'text-gray-700');
    });

    // Show selected section
    document.getElementById(`section-${mode}`).classList.remove('hidden');
    
    // Highlight selected tab
    const activeTab = document.getElementById(`tab-${mode}`);
    activeTab.classList.remove('bg-gray-200', 'text-gray-700');
    activeTab.classList.add('bg-blue-600', 'text-white');

    hideStatus();
}

function showStatus(message, isError = false) {
    statusMessage.textContent = message;
    statusMessage.classList.remove('hidden', 'bg-red-100', 'text-red-700', 'bg-blue-100', 'text-blue-700');
    if (isError) {
        statusMessage.classList.add('bg-red-100', 'text-red-700');
    } else {
        statusMessage.classList.add('bg-blue-100', 'text-blue-700');
    }
}

function hideStatus() {
    statusMessage.classList.add('hidden');
}

function setLoading(button, isLoading, originalText) {
    if (isLoading) {
        button.disabled = true;
        button.classList.add('opacity-75', 'cursor-not-allowed');
        button.innerHTML = `<span class="spinner"></span> Processing...`;
    } else {
        button.disabled = false;
        button.classList.remove('opacity-75', 'cursor-not-allowed');
        button.innerHTML = `<span>${originalText}</span>`;
    }
}

// Helper to make API calls
async function callApi(endpoint, body) {
    const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(body)
    });
    const data = await response.json();
    if (!response.ok) {
        throw new Error(data.error || 'Something went wrong');
    }
    return data;
}

// File Upload Logic
document.querySelectorAll('.file-upload').forEach(input => {
    input.addEventListener('change', async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        const targetId = e.target.getAttribute('data-target');
        const targetTextArea = document.getElementById(targetId);
        const statusSpan = e.target.closest('.flex').querySelector('.file-upload-status');

        statusSpan.textContent = "Extracting text... (This may take a moment)";
        statusSpan.className = "text-xs font-semibold file-upload-status text-blue-500";

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('/api/extract-text', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Failed to extract text');
            }

            targetTextArea.value = data.text;
            statusSpan.textContent = "Text extracted successfully!";
            statusSpan.className = "text-xs font-semibold file-upload-status text-green-500";
        } catch (error) {
            statusSpan.textContent = `Error: ${error.message}`;
            statusSpan.className = "text-xs font-semibold file-upload-status text-red-500";
        } finally {
            e.target.value = ''; // Reset input so same file can be uploaded again if needed
            setTimeout(() => {
                if (statusSpan.textContent.includes('successfully')) {
                    statusSpan.textContent = '';
                }
            }, 4000);
        }
    });
});


// Tool 1: Summarize
document.getElementById('btn-summarize').addEventListener('click', async () => {
    const input = document.getElementById('summarize-input').value.trim();
    if (input.length < 20) {
        showStatus("Please enter at least 20 characters.", true);
        return;
    }

    hideStatus();
    const btn = document.getElementById('btn-summarize');
    setLoading(btn, true, 'Summarize Text');
    
    try {
        const data = await callApi('/api/summarize', { text: input });
        const outputDiv = document.getElementById('summarize-output');
        outputDiv.classList.remove('hidden');
        renderContent(outputDiv.querySelector('.markdown-body'), data.result);
    } catch (error) {
        showStatus(error.message, true);
    } finally {
        setLoading(btn, false, 'Summarize Text');
    }
});

// Tool 2: Active Recall Quiz
document.getElementById('btn-generate-quiz').addEventListener('click', async () => {
    originalStudyMaterial = document.getElementById('quiz-input').value.trim();
    if (originalStudyMaterial.length < 50) {
        showStatus("Please provide more notes to generate a valid quiz (min 50 characters).", true);
        return;
    }

    hideStatus();
    const btn = document.getElementById('btn-generate-quiz');
    setLoading(btn, true, 'Generate Quiz Question');

    try {
        const data = await callApi('/api/quiz/generate', { text: originalStudyMaterial });
        currentQuizQuestion = data.question;
        
        // Update UI
        document.getElementById('quiz-step-1').classList.add('hidden');
        document.getElementById('quiz-step-2').classList.remove('hidden');
        document.getElementById('quiz-question-display').textContent = currentQuizQuestion;
    } catch (error) {
        showStatus(error.message, true);
    } finally {
        setLoading(btn, false, 'Generate Quiz Question');
    }
});

document.getElementById('btn-submit-answer').addEventListener('click', async () => {
    const studentAnswer = document.getElementById('quiz-answer').value.trim();
    if (!studentAnswer) {
        showStatus("Please attempt an answer before submitting.", true);
        return;
    }

    hideStatus();
    const btn = document.getElementById('btn-submit-answer');
    setLoading(btn, true, 'Submit Answer');

    try {
        const data = await callApi('/api/quiz/evaluate', {
            material: originalStudyMaterial,
            question: currentQuizQuestion,
            answer: studentAnswer
        });

        const outputDiv = document.getElementById('quiz-evaluation-output');
        outputDiv.classList.remove('hidden');
        renderContent(outputDiv.querySelector('.markdown-body'), data.evaluation);
    } catch (error) {
        showStatus(error.message, true);
    } finally {
        setLoading(btn, false, 'Submit Answer');
    }
});

document.getElementById('btn-reset-quiz').addEventListener('click', () => {
    document.getElementById('quiz-step-1').classList.remove('hidden');
    document.getElementById('quiz-step-2').classList.add('hidden');
    document.getElementById('quiz-input').value = '';
    document.getElementById('quiz-answer').value = '';
    document.getElementById('quiz-evaluation-output').classList.add('hidden');
    originalStudyMaterial = '';
    currentQuizQuestion = '';
    hideStatus();
});

// Tool 3: Draft Polisher
document.getElementById('btn-polish').addEventListener('click', async () => {
    const input = document.getElementById('polish-input').value.trim();
    if (input.length < 20) {
        showStatus("Please enter at least 20 characters.", true);
        return;
    }

    hideStatus();
    const btn = document.getElementById('btn-polish');
    setLoading(btn, true, 'Polish Draft');
    
    try {
        const data = await callApi('/api/polish', { text: input });
        const outputDiv = document.getElementById('polish-output');
        outputDiv.classList.remove('hidden');
        renderContent(outputDiv.querySelector('.markdown-body'), data.result);
    } catch (error) {
        showStatus(error.message, true);
    } finally {
        setLoading(btn, false, 'Polish Draft');
    }
});

// Tool 4: Ask a Tutor
document.getElementById('btn-ask').addEventListener('click', async () => {
    const input = document.getElementById('ask-input').value.trim();
    if (input.length < 10) {
        showStatus("Please ask a detailed question (at least 10 characters).", true);
        return;
    }

    hideStatus();
    const btn = document.getElementById('btn-ask');
    setLoading(btn, true, 'Ask Question');
    
    try {
        const data = await callApi('/api/ask', { question: input });
        const outputDiv = document.getElementById('ask-output');
        outputDiv.classList.remove('hidden');
        renderContent(outputDiv.querySelector('.markdown-body'), data.result);
    } catch (error) {
        showStatus(error.message, true);
    } finally {
        setLoading(btn, false, 'Ask Question');
    }
});
