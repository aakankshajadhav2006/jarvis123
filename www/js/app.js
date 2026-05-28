/**
 * J.A.R.V.I.S. Frontend Application
 * Handles UI interactions and Eel integration for Python backend
 */

// ============================================
// Global State
// ============================================
const AppState = {
    currentLanguage: 'en',
    isListening: false,
    isVoiceModeEnabled: false,
    uploadedPDFPath: null,
    currentSummaries: null
};


// ============================================
// Initialization
// ============================================

document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    startClock();
    setupEventListeners();
});


/**
 * Initialize the application
 */
async function initializeApp() {
    try {
        // Initialize backend
        if (eel && eel.init) {
            await eel.init();
        } else {
            console.warn('Eel not available, running in standalone mode');
            hideLoader();
            showMainApp();
        }
    } catch (error) {
        console.error('Initialization error:', error);
        showStatus('error', 'Failed to initialize application');
        hideLoader();
        showMainApp();
    }
}


/**
 * Setup all event listeners
 */
function setupEventListeners() {
    // Language selector
    const languageSelect = document.getElementById('language');
    if (languageSelect) {
        languageSelect.addEventListener('change', handleLanguageChange);
    }

    // Voice controls
    const micButton = document.getElementById('mic-btn');
    if (micButton) {
        micButton.addEventListener('click', toggleListening);
    }

    const voiceToggleBtn = document.getElementById('voice-toggle-btn');
    if (voiceToggleBtn) {
        voiceToggleBtn.addEventListener('click', toggleVoiceMode);
    }

    const sendButton = document.getElementById('send-btn');
    const textCommand = document.getElementById('text-command');
    if (sendButton && textCommand) {
        sendButton.addEventListener('click', sendTextCommand);
        textCommand.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendTextCommand();
            }
        });
    }

    // PDF Summarizer
    const uploadZone = document.getElementById('upload-zone');
    const pdfInput = document.getElementById('pdf-input');
    const summarizeBtn = document.getElementById('summarize-btn');
    const removeFileBtn = document.getElementById('remove-file');
    const saveSummaryBtn = document.getElementById('save-summary-btn');
    const speakSummaryBtn = document.getElementById('speak-summary-btn');

    if (uploadZone && pdfInput) {
        uploadZone.addEventListener('click', () => pdfInput.click());
        pdfInput.addEventListener('change', handlePDFUpload);

        // Drag and drop
        uploadZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadZone.classList.add('dragover');
        });

        uploadZone.addEventListener('dragleave', () => {
            uploadZone.classList.remove('dragover');
        });

        uploadZone.addEventListener('drop', handlePDFDrop);
    }

    if (summarizeBtn) {
        summarizeBtn.addEventListener('click', summarizePDF);
    }

    if (removeFileBtn) {
        removeFileBtn.addEventListener('click', removeUploadedPDF);
    }

    if (saveSummaryBtn) {
        saveSummaryBtn.addEventListener('click', saveSummary);
    }

    if (speakSummaryBtn) {
        speakSummaryBtn.addEventListener('click', speakSummary);
    }

    // Tab navigation
    document.querySelectorAll('.tab-btn').forEach(button => {
        button.addEventListener('click', function() {
            switchTab(this.dataset.tab);
        });
    });

    // Quick actions
    document.querySelectorAll('.action-btn').forEach(button => {
        button.addEventListener('click', function() {
            handleQuickAction(this.dataset.action);
        });
    });
}


// ============================================
// Language Functions
// ============================================

/**
 * Handle language change
 */
async function handleLanguageChange(event) {
    const lang = event.target.value;

    try {
        if (eel && eel.change_language) {
            const result = await eel.change_language(lang)();
            if (result.success) {
                AppState.currentLanguage = lang;
                showStatus('success', `Language changed to ${result.language}`);
            } else {
                showStatus('error', result.error || 'Failed to change language');
            }
        }
    } catch (error) {
        console.error('Language change error:', error);
        showStatus('error', 'Error changing language');
    }
}


// ============================================
// Voice Assistant Functions
// ============================================

/**
 * Toggle listening state
 */
function toggleListening() {
    const micButton = document.getElementById('mic-btn');
    const visualizer = document.getElementById('audio-visualizer');

    AppState.isListening = !AppState.isListening;

    if (AppState.isListening) {
        micButton.classList.add('listening');
        visualizer.classList.add('active');
        startVoiceRecognition();
    } else {
        micButton.classList.remove('listening');
        visualizer.classList.remove('active');
        stopVoiceRecognition();
    }
}


/**
 * Start voice recognition
 */
async function startVoiceRecognition() {
    try {
        updateResponse('Listening... Speak now');

        if (eel && eel.process_voice_command) {
            const result = await eel.process_voice_command(AppState.currentLanguage)();
            handleCommandResult(result);
        } else {
            // Fallback for standalone testing
            setTimeout(() => {
                handleCommandResult({ success: true, response: 'Voice recognition simulation successful' });
            }, 2000);
        }
    } catch (error) {
        console.error('Voice recognition error:', error);
        updateResponse('Error in voice recognition');
        toggleListening();
    }
}


/**
 * Stop voice recognition
 */
function stopVoiceRecognition() {
    updateResponse('Stopped listening');
}


/**
 * Send text command
 */
async function sendTextCommand() {
    const input = document.getElementById('text-command');
    const command = input.value.trim();

    if (!command) {
        return;
    }

    try {
        updateResponse(`You said: "${command}"`);

        if (eel && eel.process_user_command) {
            const result = await eel.process_user_command(command)();
            handleCommandResult(result);
        } else {
            // Fallback for testing
            handleCommandResult({ success: true, response: `Command "${command}" received` });
        }

        input.value = '';
    } catch (error) {
        console.error('Command error:', error);
        updateResponse('Error processing command');
    }
}


/**
 * Handle command result
 */
function handleCommandResult(result) {
    if (result.success) {
        updateResponse(result.response || result.message || 'Command executed');
    } else {
        updateResponse(result.error || 'Command failed');
    }
}


/**
 * Toggle voice mode
 */
function toggleVoiceMode() {
    AppState.isVoiceModeEnabled = !AppState.isVoiceModeEnabled;

    const btn = document.getElementById('voice-toggle-btn');
    if (btn) {
        btn.classList.toggle('active', AppState.isVoiceModeEnabled);
    }

    showStatus('success', `Voice mode ${AppState.isVoiceModeEnabled ? 'enabled' : 'disabled'}`);
}


// ============================================
// PDF Summarizer Functions
// ============================================

/**
 * Handle PDF upload
 */
async function handlePDFUpload(event) {
    const file = event.target.files[0];
    if (file && file.type === 'application/pdf') {
        await processPDFUpload(file);
    } else {
        showStatus('error', 'Please select a valid PDF file');
    }
}


/**
 * Handle PDF drop
 */
async function handlePDFDrop(event) {
    event.preventDefault();
    event.stopPropagation();

    const uploadZone = document.getElementById('upload-zone');
    uploadZone.classList.remove('dragover');

    const file = event.dataTransfer.files[0];
    if (file && file.type === 'application/pdf') {
        await processPDFUpload(file);
    } else {
        showStatus('error', 'Please drop a valid PDF file');
    }
}


/**
 * Process uploaded PDF
 */
async function processPDFUpload(file) {
    try {
        showStatus('success', 'Uploading PDF...');

        // Read file as base64
        const fileData = await readFileAsBase64(file);

        if (eel && eel.save_uploaded_pdf) {
            const result = await eel.save_uploaded_pdf(fileData, file.name)();

            if (result.success) {
                AppState.uploadedPDFPath = result.file_path;
                displayFileInfo(file.name);
                enableSummarizeButton();
                showStatus('success', 'PDF uploaded successfully');
            } else {
                showStatus('error', result.error || 'Upload failed');
            }
        } else {
            // Fallback for testing
            AppState.uploadedPDFPath = file.name;
            displayFileInfo(file.name);
            enableSummarizeButton();
            showStatus('success', 'PDF ready for testing');
        }
    } catch (error) {
        console.error('Upload error:', error);
        showStatus('error', 'Failed to upload PDF');
    }
}


/**
 * Read file as base64
 */
function readFileAsBase64(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve(reader.result);
        reader.onerror = reject;
        reader.readAsDataURL(file);
    });
}


/**
 * Summarize PDF
 */
async function summarizePDF() {
    if (!AppState.uploadedPDFPath) {
        showStatus('error', 'No PDF uploaded');
        return;
    }

    try {
        showStatus('success', 'Generating summary... This may take a moment');

        if (eel && eel.summarize_pdf) {
            const result = await eel.summarize_pdf(AppState.uploadedPDFPath)();

            if (result.success) {
                displaySummaryResults(result);
                AppState.currentSummaries = result;
                showStatus('success', 'Summary generated successfully');
            } else {
                showStatus('error', result.error || 'Summarization failed');
            }
        } else {
            // Fallback for testing
            const testResult = {
                success: true,
                summary: 'This is a test summary of the document.',
                key_points: '- Point 1\n- Point 2\n- Point 3',
                viva_questions: 'Q1: Test question 1?\nQ2: Test question 2?'
            };
            displaySummaryResults(testResult);
            AppState.currentSummaries = testResult;
            showStatus('success', 'Test summary generated');
        }
    } catch (error) {
        console.error('Summarization error:', error);
        showStatus('error', 'Failed to generate summary');
    }
}


/**
 * Display file info
 */
function displayFileInfo(fileName) {
    const fileInfo = document.getElementById('file-info');
    const fileNameEl = document.getElementById('file-name');
    const uploadZone = document.getElementById('upload-zone');

    if (fileInfo && fileNameEl) {
        fileNameEl.textContent = fileName;
        fileInfo.classList.remove('hidden');
        uploadZone.classList.add('hidden');
    }
}


/**
 * Remove uploaded PDF
 */
function removeUploadedPDF() {
    AppState.uploadedPDFPath = null;

    const fileInfo = document.getElementById('file-info');
    const uploadZone = document.getElementById('upload-zone');
    const pdfInput = document.getElementById('pdf-input');
    const summaryResults = document.getElementById('summary-results');

    if (fileInfo) fileInfo.classList.add('hidden');
    if (uploadZone) uploadZone.classList.remove('hidden');
    if (pdfInput) pdfInput.value = '';
    if (summaryResults) summaryResults.classList.add('hidden');

    disableSummarizeButton();
    showStatus('success', 'PDF removed');
}


/**
 * Display summary results
 */
function displaySummaryResults(result) {
    const summaryResults = document.getElementById('summary-results');
    const summaryText = document.getElementById('summary-text');
    const keyPointsText = document.getElementById('key-points-text');
    const vivaQuestionsText = document.getElementById('viva-questions-text');

    if (summaryText) summaryText.textContent = result.summary;
    if (keyPointsText) keyPointsText.textContent = result.key_points;
    if (vivaQuestionsText) vivaQuestionsText.textContent = result.viva_questions;

    if (summaryResults) {
        summaryResults.classList.remove('hidden');
    }
}


/**
 * Save summary to database
 */
async function saveSummary() {
    if (!AppState.currentSummaries) {
        showStatus('error', 'No summary to save');
        return;
    }

    try {
        if (eel && eel.save_pdf_summary) {
            const result = await eel.save_pdf_summary(AppState.currentSummaries)();
            if (result.success) {
                showStatus('success', 'Summary saved successfully');
            } else {
                showStatus('error', result.error || 'Failed to save');
            }
        } else {
            showStatus('success', 'Summary saved (simulation)');
        }
    } catch (error) {
        console.error('Save error:', error);
        showStatus('error', 'Failed to save summary');
    }
}


/**
 * Speak summary aloud
 */
async function speakSummary() {
    if (!AppState.currentSummaries) {
        showStatus('error', 'No summary to speak');
        return;
    }

    const summaryText = AppState.currentSummaries.summary;

    try {
        if (eel && eel.speak_multilingual) {
            const result = await eel.speak_multilingual(summaryText, AppState.currentLanguage)();
            if (result.success) {
                showStatus('success', 'Speaking summary...');
            } else {
                showStatus('error', result.error || 'Failed to speak');
            }
        } else {
            // Browser TTS fallback
            if ('speechSynthesis' in window) {
                const utterance = new SpeechSynthesisUtterance(summaryText);
                speechSynthesis.speak(utterance);
                showStatus('success', 'Speaking summary...');
            } else {
                showStatus('error', 'Speech synthesis not supported');
            }
        }
    } catch (error) {
        console.error('Speak error:', error);
        showStatus('error', 'Failed to speak summary');
    }
}


/**
 * Enable/disable summarize button
 */
function enableSummarizeButton() {
    const btn = document.getElementById('summarize-btn');
    if (btn) btn.disabled = false;
}

function disableSummarizeButton() {
    const btn = document.getElementById('summarize-btn');
    if (btn) btn.disabled = true;
}


// ============================================
// Tab Navigation
// ============================================

/**
 * Switch active tab
 */
function switchTab(tabId) {
    // Hide all tab contents
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.add('hidden');
    });

    // Show selected tab
    const selectedTab = document.getElementById(tabId);
    if (selectedTab) {
        selectedTab.classList.remove('hidden');
    }

    // Update button states
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.tab === tabId);
    });
}


// ============================================
// Quick Actions
// ============================================

/**
 * Handle quick action button
 */
async function handleQuickAction(action) {
    const commands = {
        'time': 'what time is it',
        'date': 'what is the date today',
        'weather': 'what is the weather',
        'youtube': 'open youtube',
        'google': 'open google',
        'wikipedia': 'search wikipedia'
    };

    const command = commands[action] || action;
    const input = document.getElementById('text-command');
    if (input) input.value = command;

    await sendTextCommand();
}


// ============================================
// UI Helper Functions
// ============================================

/**
 * Show status message
 */
function showStatus(type, message) {
    const statusDiv = document.getElementById('pdf-status');
    if (!statusDiv) return;

    statusDiv.textContent = message;
    statusDiv.className = `status-message ${type}`;
    statusDiv.classList.remove('hidden');

    setTimeout(() => {
        statusDiv.classList.add('hidden');
    }, 3000);
}


/**
 * Update response area
 */
function updateResponse(message) {
    const responseArea = document.getElementById('response-area');
    if (responseArea) {
        responseArea.innerHTML = `<p class="response-text">${message}</p>`;
    }
}


/**
 * Hide loader
 */
function hideLoader() {
    const loader = document.getElementById('loader');
    if (loader) loader.classList.add('hidden');
}


/**
 * Show main app
 */
function showMainApp() {
    const mainApp = document.getElementById('main-app');
    if (mainApp) mainApp.classList.remove('hidden');
}


/**
 * Hide face auth
 */
function hideFaceAuth() {
    const faceAuth = document.getElementById('face-auth');
    if (faceAuth) faceAuth.classList.add('hidden');
}


/**
 * Start clock
 */
function startClock() {
    function updateClock() {
        const clockElement = document.getElementById('clock');
        if (clockElement) {
            const now = new Date();
            clockElement.textContent = now.toLocaleTimeString('en-US', { hour12: false });
        }
    }

    updateClock();
    setInterval(updateClock, 1000);
}


// ============================================
// Eel-exposed Functions (called from Python)
// ============================================

function hideLoader() {
    const loader = document.getElementById('loader');
    if (loader) {
        loader.classList.add('hidden');
    }
}

function hideFaceAuth() {
    const faceAuth = document.getElementById('face-auth');
    if (faceAuth) {
        faceAuth.classList.add('hidden');
    }
}

function hideFaceAuthSuccess() {
    // Can add success animation here
}

function hideStart() {
    const mainApp = document.getElementById('main-app');
    if (mainApp) {
        mainApp.classList.remove('hidden');
    }
}

// Expose functions to Eel
if (typeof eel !== 'undefined') {
    eel.expose(hideLoader);
    eel.expose(hideFaceAuth);
    eel.expose(hideFaceAuthSuccess);
    eel.expose(hideStart);
}
