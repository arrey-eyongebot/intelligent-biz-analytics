const API_BASE = 'http://127.0.0.1:5000/api';

const fileInput  = document.getElementById('file-input');
const uploadBtn  = document.getElementById('upload-btn');
const fileNameEl = document.getElementById('file-name');
const statusBox  = document.getElementById('status-box');
const statusContent = document.getElementById('status-content');

// Show selected file name
fileInput.addEventListener('change', () => {
    const file = fileInput.files[0];
    if (file) {
        fileNameEl.textContent = file.name;
        uploadBtn.disabled = false;
    }
});

// Drag and drop
const uploadBox = document.getElementById('upload-box');
uploadBox.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadBox.style.background = '#eff6ff';
});

uploadBox.addEventListener('drop', (e) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (file) {
        fileInput.files = e.dataTransfer.files;
        fileNameEl.textContent = file.name;
        uploadBtn.disabled = false;
    }
});

// Upload file
uploadBtn.addEventListener('click', async () => {
    const file = fileInput.files[0];
    if (!file) return;

    // Show loading
    statusBox.style.display = 'block';
    statusContent.innerHTML = '<div class="spinner"></div><p>Uploading and analyzing your data...</p>';
    uploadBtn.disabled = true;

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch(`${API_BASE}/upload/`, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (response.ok) {
            statusContent.innerHTML = `
                <p class="status-success">
                    <i class="fas fa-check-circle"></i>
                    File uploaded successfully!
                </p>
                <p>📊 <strong>${data.rows}</strong> rows processed</p>
                <p>📁 Columns found: <strong>${data.columns.join(', ')}</strong></p>
                <br>
                <a href="dashboard.html" class="btn-primary">
                    <i class="fas fa-chart-bar"></i> View Dashboard
                </a>
            `;
        } else {
            statusContent.innerHTML = `
                <p class="status-error">
                    <i class="fas fa-times-circle"></i>
                    Error: ${data.error}
                </p>
            `;
        }
    } catch (err) {
        statusContent.innerHTML = `
            <p class="status-error">
                <i class="fas fa-times-circle"></i>
                Could not connect to server. Make sure the backend is running.
            </p>
        `;
    }

    uploadBtn.disabled = false;
});