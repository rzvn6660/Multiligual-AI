let mediaRecorder;
let audioChunks = [];
let isRecording = false;
let statusInterval;
// VAD Settings
let silenceStart = Date.now();
const SILENCE_THRESHOLD = 10; // Adjust sensitivity
const SILENCE_DURATION = 1000; // 1 second
let vadInterval;

const recordBtn = document.getElementById('recordBtn');
const statusText = document.getElementById('statusText');
const messagesDiv = document.getElementById('messages');
const visualizerCanvas = document.getElementById('visualizer');
const canvasCtx = visualizerCanvas.getContext('2d');

// Status Dots
const statusDots = {
    asr: document.getElementById('asrStatus'),
    mt: document.getElementById('mtStatus'),
    tts: document.getElementById('ttsStatus')
};

// Check Backend Status
async function checkStatus() {
    try {
        const res = await fetch('/api/status');
        const data = await res.json();

        statusDots.asr.classList.toggle('active', data.asr);
        statusDots.mt.classList.toggle('active', data.mt);
        statusDots.tts.classList.toggle('active', data.tts);

        if (!data.asr) {
            let msg = "ASR Offline";
            if (data.errors && data.errors.asr) msg += `: ${data.errors.asr}`;
            addSystemMessage(msg);
            statusDots.asr.title = msg;
        }

        if (data.errors && data.errors.mt) statusDots.mt.title = data.errors.mt;
        if (data.errors && data.errors.tts) statusDots.tts.title = data.errors.tts;

    } catch (e) {
        console.error("Backend offline", e);
        addSystemMessage("Server Offline or Unreachable");
    }
}
checkStatus();

// Load Chat History
async function loadHistory() {
    try {
        const res = await fetch('/api/history');
        const history = await res.json();

        // Clear default welcome message if history exists
        if (history && history.length > 0) {
            const defaultMsg = document.querySelector('.message.system');
            if (defaultMsg && defaultMsg.innerText.includes("Welcome")) {
                defaultMsg.remove();
            }
        }

        if (history) {
            history.forEach(item => {
                // User Message
                addMessage('user', item.query_santali);

                // Bot Message (with debug info)
                const debugObj = {
                    asr_text: item.query_santali,
                    english_in: item.query_english,
                    english_out: item.response_english,
                    santali_out: item.response_santali
                };
                addMessage('bot', item.response_santali, debugObj);
            });

            // Scroll to bottom after loading
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }

    } catch (e) {
        console.error("Failed to load history", e);
    }
}

loadHistory();

// Clear History
const clearBtn = document.getElementById('clearHistoryBtn');
if (clearBtn) {
    clearBtn.addEventListener('click', async () => {
        if (confirm("Are you sure you want to clear all chat history?")) {
            try {
                await fetch('/api/history', { method: 'DELETE' });
                // Clear UI
                const msgs = document.querySelectorAll('.message:not(.system)');
                msgs.forEach(m => m.remove());
                addSystemMessage("History Cleared.");
            } catch (e) {
                console.error("Clear failed", e);
                addSystemMessage("Failed to clear history.");
            }
        }
    });
}

// Audio Context for Visualization
let audioCtx;
let analyser;
let dataArray;
let source;

function initAudioContext() {
    if (!audioCtx) {
        audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        analyser = audioCtx.createAnalyser();
        analyser.fftSize = 256;
        const bufferLength = analyser.frequencyBinCount;
        dataArray = new Uint8Array(bufferLength);
    }
}

// Draw Visualizer
function drawVisualizer() {
    requestAnimationFrame(drawVisualizer);

    if (!analyser) return;
    analyser.getByteFrequencyData(dataArray);

    canvasCtx.fillStyle = '#0f172a'; // Clear with bg color
    canvasCtx.fillRect(0, 0, visualizerCanvas.width, visualizerCanvas.height);

    const barWidth = (visualizerCanvas.width / dataArray.length) * 2.5;
    let barHeight;
    let x = 0;

    // VAD Logic within Visualizer Loop for efficiency
    let sum = 0;
    for (let i = 0; i < dataArray.length; i++) {
        sum += dataArray[i];
    }
    const average = sum / dataArray.length;

    // Drawing
    for (let i = 0; i < dataArray.length; i++) {
        barHeight = dataArray[i] / 2;
        // Visual feedback for voice activity
        if (average > SILENCE_THRESHOLD) {
            canvasCtx.fillStyle = `rgb(${barHeight + 100}, 50, 50)`; // Red tint when speaking
        } else {
            canvasCtx.fillStyle = `rgb(${barHeight + 100}, 189, 248)`;
        }
        canvasCtx.fillRect(x, visualizerCanvas.height - barHeight, barWidth, barHeight);
        x += barWidth + 1;
    }

    // Check Silence
    if (isRecording) {
        if (average > SILENCE_THRESHOLD) {
            silenceStart = Date.now(); // Reset timer
            statusText.innerText = "Listening...";
        } else if (Date.now() - silenceStart > SILENCE_DURATION) {
            console.log("Silence detected, stopping...");
            stopRecording();
        }
    }
}


// Input Mode Logic
const inputMicRadio = document.getElementById('inputMic');
const inputFileRadio = document.getElementById('inputFile');
const fileInput = document.getElementById('fileInput');
const inputIcon = document.getElementById('inputIcon');
let inputMode = 'mic';


function updateInputMode() {
    // Safety: Stop recording if active when switching
    if (isRecording) {
        stopRecording();
    }

    if (inputFileRadio.checked) {
        inputMode = 'file';
        inputIcon.className = 'fas fa-file-upload';
        recordBtn.title = "Click to Upload Audio";
        statusText.innerText = "Upload Mode";
    } else {
        inputMode = 'mic';
        inputIcon.className = 'fas fa-microphone';
        recordBtn.title = "Hold/Click to Record";
        statusText.innerText = "Tap to Speak";
    }
}

inputMicRadio.addEventListener('change', updateInputMode);
inputFileRadio.addEventListener('change', updateInputMode);

// Initialize state
updateInputMode();

// File Upload Handling
fileInput.addEventListener('change', async (e) => {
    if (e.target.files.length > 0) {
        const file = e.target.files[0];
        statusText.innerText = "Uploading...";
        await sendAudioToBackend(file);
        // Reset input so same file can be selected again if needed
        fileInput.value = '';
    }
});

// Recording Logic
recordBtn.addEventListener('click', async () => {
    if (inputMode === 'file') {
        fileInput.click();
        return;
    }

    if (!isRecording) {
        startRecording();
    } else {
        stopRecording();
    }
});

async function startRecording() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

        initAudioContext();
        source = audioCtx.createMediaStreamSource(stream);
        source.connect(analyser);
        drawVisualizer();

        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];

        mediaRecorder.ondataavailable = event => {
            audioChunks.push(event.data);
        };

        mediaRecorder.onstop = async () => {
            const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
            sendAudioToBackend(audioBlob);

            // Stop tracks
            stream.getTracks().forEach(track => track.stop());
        };

        mediaRecorder.start();
        isRecording = true;
        silenceStart = Date.now(); // Initialize silence timer
        recordBtn.classList.add('recording');
        recordBtn.innerHTML = '<i class="fas fa-stop"></i>';
        statusText.innerText = "Listening...";

    } catch (err) {
        console.error("Mic Error:", err);
        addSystemMessage("Microphone access denied.");
    }
}

// Simulated Progress Steps
function startProcessingSim() {
    let steps = ["Uploading...", "Transcribing (Santali)...", "Translating to English...", "AI Thinking...", "Translating to Santali...", "Generating Voice..."];
    let i = 0;
    statusText.innerText = steps[0];
    statusInterval = setInterval(() => {
        i = (i + 1) % steps.length;
        statusText.innerText = steps[i];
    }, 800); // Faster updates (0.8s) to make UI feel more responsive
}

function stopProcessingSim() {
    clearInterval(statusInterval);
}

function stopRecording() {
    if (mediaRecorder && isRecording) {
        mediaRecorder.stop();
        isRecording = false;
        recordBtn.classList.remove('recording');
        statusText.innerText = "Processing...";
        startProcessingSim(); // Start visual feedback
    }
}

async function sendAudioToBackend(blob) {
    const formData = new FormData();
    formData.append('audio', blob, 'input.wav');

    const modeSelect = document.getElementById('modeSelect');
    if (modeSelect) {
        formData.append('mode', modeSelect.value);
    }

    try {
        // Show temp message with spinner
        addMessage('user', '<i class="fas fa-spinner fa-spin"></i> Processing...', null);

        const response = await fetch('/api/process', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.error) {
            addSystemMessage(`Error: ${data.error}`);
            statusText.innerText = "Error occurred";
        } else {
            // Update last user message
            const lastMsg = document.querySelector('.message.user:last-child');
            if (lastMsg) lastMsg.remove();

            addMessage('user', data.query_santali);

            const debugObj = {
                asr_text: data.query_santali,
                english_in: data.query_english,
                english_out: data.response_english,
                santali_out: data.response_santali
            };
            addMessage('bot', data.response_santali, debugObj);

            if (data.audio_url) {
                const audioControls = document.getElementById('audio-controls');
                const audioPlayer = document.getElementById('responseAudio');
                const playBtn = document.getElementById('playResponseBtn');

                // Update button state
                playBtn.disabled = false;
                // Add a glow effect or change icon color to indicate readiness if needed via CSS classes, 
                // but default enabled state is enough.

                // Set audio source with timestamp
                audioPlayer.src = data.audio_url + "?t=" + new Date().getTime();

                // Set up button click
                playBtn.onclick = () => {
                    audioPlayer.play();
                };

                // Check Auto-Play
                const autoPlayCheckbox = document.getElementById('autoPlayToggle');
                if (autoPlayCheckbox && autoPlayCheckbox.checked) {
                    console.log("Auto-playing response...");
                    setTimeout(() => {
                        audioPlayer.play().catch(e => {
                            console.log("Auto-play blocked:", e);
                            addSystemMessage("Click Play to listen.");
                        });
                    }, 500);
                }
            } // End audio logic
        } // End else (success)
        stopProcessingSim();
        statusText.innerText = "Reply Sent";
    } catch (err) {
        console.error(err);
        stopProcessingSim();
        addSystemMessage("Network Error");
        statusText.innerText = "Offline?";
    }
}

// Enhanced addMessage to support multi-stage display
function addMessage(type, primaryText, debugInfo = null) {
    const div = document.createElement('div');
    div.className = `message ${type}`;

    let content = `<div class="primary">${primaryText}</div>`;

    // If we have debug info (only for bot usually), render the grid
    if (debugInfo) {
        content += `
            <div class="debug-grid">
                <div class="debug-item">
                    <span class="debug-label">1. ASR (Input)</span>
                    ${debugInfo.asr_text || '-'}
                </div>
                <div class="debug-item">
                    <span class="debug-label">2. MT (To Eng)</span>
                    ${debugInfo.english_in || '-'}
                </div>
                <div class="debug-item">
                    <span class="debug-label">3. AI Reason (Eng)</span>
                    ${debugInfo.english_out || '-'}
                </div>
                <div class="debug-item">
                    <span class="debug-label">4. MT (Reply)</span>
                    ${debugInfo.santali_out || '-'}
                </div>
            </div>
        `;
    }

    div.innerHTML = content;
    messagesDiv.appendChild(div);

    // Smooth scroll to the new message
    div.scrollIntoView({ behavior: 'smooth', block: 'end' });
}


function addSystemMessage(text) {
    const div = document.createElement('div');
    div.className = `message system`;
    div.innerText = text;
    messagesDiv.appendChild(div);
}

// Scroll Button Logic
const scrollBtn = document.getElementById('scrollBtn');

messagesDiv.addEventListener('scroll', () => {
    // Show button if we are not at the bottom
    const isAtBottom = messagesDiv.scrollHeight - messagesDiv.scrollTop <= messagesDiv.clientHeight + 50;

    if (isAtBottom) {
        scrollBtn.classList.add('hidden');
    } else {
        scrollBtn.classList.remove('hidden');
    }
});

scrollBtn.addEventListener('click', () => {
    messagesDiv.scrollTo({
        top: messagesDiv.scrollHeight,
        behavior: 'smooth'
    });
});
