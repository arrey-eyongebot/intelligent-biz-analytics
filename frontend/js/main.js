// ============================================================
// main.js — Upload Page Logic
// Handles file selection, drag and drop, and file upload.
// Sends the selected file to the backend API and displays
// the response (success or error) to the user.
// ============================================================

// Base URL for all backend API calls
// Change this when deploying to production
const API_BASE = 'http://127.0.0.1:5000/api';

// ── Get References to HTML Elements ─────────────────────────
// We grab these elements once and reuse them throughout
const fileInput     = document.getElementById('file-input');     // Hidden file input
const uploadBtn     = document.getElementById('upload-btn');     // Upload button
const fileNameEl    = document.getElementById('file-name');      // File name display
const statusBox     = document.getElementById('status-box');     // Result container
const statusContent = document.getElementById('status-content'); // Result content


// ── Event: File Selected via Browse Button ───────────────────
// Fires when the user picks a file using the Browse button
fileInput.addEventListener('change', () => {
    const file = fileInput.files[0]; // Get the first selected file
    if (file) {
        fileNameEl.textContent  = file.name; // Show the file name
        uploadBtn.disabled      = false;     // Enable the upload button
    }
});


// ── Event: Drag Over the Upload Box ─────────────────────────
// Fires when a file is dragged over the upload box
// We must call preventDefault() to allow the drop event
const uploadBox = document.getElementById('upload-box');
uploadBox.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadBox.style.background = '#eff6ff'; // Highlight box on drag
});


// ── Event: File Dropped onto Upload Box ─────────────────────
// Fires when the user drops a file onto the upload box
uploadBox.addEventListener('drop', (e) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0]; // Get the dropped file
    if (file) {
        fileInput.files        = e.dataTransfer.files; // Assign to input
        fileNameEl.textContent = file.name;            // Show file name
        uploadBtn.disabled     = false;                // Enable upload button
    }
});


// ── Event: Upload Button Clicked ─────────────────────────────
// Fires when the user clicks "Upload & Analyze"
// Sends the file to the backend and handles the response
uploadBtn.addEventListener('click', async () => {
    const file = fileInput.files[0];
    if (!file) return; // Do nothing if no file selected

    // Show loading spinner while waiting for backend response
    statusBox.style.display  = 'block';
    statusContent.innerHTML  = `
        <div class="spinner"></div>
        <p>Uploading and analyzing your data...</p>
    `;
    uploadBtn.disabled = true; // Prevent double clicks

    // Build a FormData object to send the file as multipart/form-data
    const formData = new FormData();
    formData.append('file', file);

    try {
        // Send POST request to the upload endpoint
        const response = await fetch(`${API_BASE}/upload/`, {
            method: 'POST',
            body:   formData
        });

        const data = await response.json(); // Parse the JSON response

        if (response.ok) {
            // ── Success: Show upload summary and link to dashboard
            statusContent.innerHTML = `
                <p class="status-success">
                    <i class="fas fa-check-circle"></i>
                    File uploaded successfully!
                </p>
                <p>📊 <strong>${data.rows}</strong> rows processed</p>
                <p>📁 Columns found:
                    <strong>${data.columns.join(', ')}</strong>
                </p>
                <br>
                <a href="dashboard.html" class="btn-primary">
                    <i class="fas fa-chart-bar"></i> View Dashboard
                </a>
            `;
        } else {
            // ── Backend returned an error (e.g. wrong file type)
            statusContent.innerHTML = `
                <p class="status-error">
                    <i class="fas fa-times-circle"></i>
                    Error: ${data.error}
                </p>
            `;
        }

    } catch (err) {
        // ── Network error: backend is not running or unreachable
        statusContent.innerHTML = `
            <p class="status-error">
                <i class="fas fa-times-circle"></i>
                Could not connect to server.
                Make sure the backend is running.
            </p>
        `;
    }

    uploadBtn.disabled = false; // Re-enable button after response
});