document.addEventListener('DOMContentLoaded', () => {
    const recordBtn = document.getElementById('record-btn');
    const statusText = document.getElementById('status-text');
    const chatContainer = document.getElementById('chat-container');
    const visualizer = document.getElementById('visualizer');

    let isRecording = false;
    let mediaRecorder;
    let audioChunks = [];

    recordBtn.addEventListener('click', toggleRecording);

    async function toggleRecording() {
        if (!isRecording) {
            // Start Recording
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                mediaRecorder = new MediaRecorder(stream);
                audioChunks = [];

                mediaRecorder.ondataavailable = event => {
                    audioChunks.push(event.data);
                };

                mediaRecorder.onstop = sendAudioToServer;

                mediaRecorder.start();
                isRecording = true;
                updateUIState('recording');
            } catch (err) {
                console.error("Error accessing microphone:", err);
                alert("Could not access microphone. Please check permissions.");
            }
        } else {
            // Stop Recording
            mediaRecorder.stop();
            isRecording = false;
            updateUIState('processing');
        }
    }

    function updateUIState(state) {
        if (state === 'recording') {
            recordBtn.classList.add('recording');
            visualizer.classList.add('active');
            statusText.textContent = "Listening...";
        } else if (state === 'processing') {
            recordBtn.classList.remove('recording');
            visualizer.classList.remove('active');
            statusText.textContent = "Processing...";
            // recordBtn.disabled = true;
        } else if (state === 'idle') {
            recordBtn.classList.remove('recording');
            statusText.textContent = "Tap to Speak";
            recordBtn.disabled = false;
        }
    }

    async function sendAudioToServer() {
        // Prepare file
        const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
        const formData = new FormData();
        formData.append("file", audioBlob, "input.wav");

        try {
            // Add skeleton buffer message
            addMessage("...", "user", true);

            const response = await fetch('/process-audio/', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error("Server error");
            }

            const data = await response.json();

            // Remove skeleton
            removeLastMessage();

            // 1. Show User's Recognized Text
            if (data.user_text) {
                addMessage(data.user_text, 'user', false, data.user_trans);
            }

            // 2. Show AI Response
            if (data.ai_text) {
                setTimeout(() => {
                    addMessage(data.ai_text, 'ai', false, data.ai_trans, data.
                        audio_url);

                    // Auto play audio
                    if (data.audio_url) {
                        const audio = new Audio(data.audio_url);
                        audio.play();
                    }
                }, 500);
            }

        } catch (error) {
            console.error(error);
            statusText.textContent = "Error occurred.";
        } finally {
            updateUIState('idle');
        }
    }

    function addMessage(text, sender, isSkeleton, translation = null, audioUrl = null) {
        const div = document.createElement('div');
        div.className = `message ${sender} ${isSkeleton ? 'skeleton' : ''}`;

        let content = `<div class="text">${text}</div>`;

        if (translation) {
            content += `<span class="translation">${translation}</span>`;
        }

        div.innerHTML = content;
        chatContainer.appendChild(div);
        chatContainer.scrollTo(0, chatContainer.scrollHeight);
    }

    function removeLastMessage() {
        const skeletons = chatContainer.querySelectorAll('.skeleton');
        if (skeletons.length > 0) {
            skeletons[skeletons.length - 1].remove();
        }
    }
});
