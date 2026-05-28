// ============================================================
// main.js — Home Page Upload & Column Mapping Logic
//
// This script handles the entire data upload workflow:
//
// STEP 1 — File Selection:
//   User picks a file via Browse button or drag-and-drop.
//   The filename is displayed and the Upload button activates.
//
// STEP 2 — Upload & Auto-Detect:
//   File is sent to POST /api/upload/ which saves it and
//   returns a suggested column mapping based on the file's
//   column names. The mapping is shown in a confirmation table.
//
// STEP 3 — Confirm Mapping:
//   User reviews and adjusts the mapping dropdowns if needed,
//   then clicks Confirm. The confirmed mapping is sent to
//   POST /api/upload/confirm which finalizes the cleaned data.
// ============================================================

// Base URL for all backend API calls
const API_BASE = 'http://127.0.0.1:5000/api';

// System columns shown in the mapping dropdown options
const EXPECTED_COLUMNS = [
    'Customer_Name', 'Sex', 'Product', 'Category',
    'Quantity', 'Date', 'Unit_Price', 'Amount', 'Channel'
];

// Stores state between Step 2 and Step 3
let uploadedFilename = '';  // Filename of the uploaded file
let currentMapping   = {};  // Auto-detected mapping result

// ── DOM Element References ────────────────────────────────────
const fileInput      = document.getElementById('file-input');
const uploadBtn      = document.getElementById('upload-btn');
const fileNameEl     = document.getElementById('file-name');
const statusBox      = document.getElementById('status-box');
const statusContent  = document.getElementById('status-content');
const mappingSection = document.getElementById('mapping-section');
const mappingTable   = document.getElementById('mapping-table');


// ── STEP 1A: File Selected via Browse Button ──────────────────
// When user picks a file, show its name and enable the upload btn
fileInput.addEventListener('change', () => {
    const file = fileInput.files[0];
    if (file) {
        fileNameEl.textContent = file.name;
        uploadBtn.disabled     = false;
    }
});


// ── STEP 1B: Drag and Drop ────────────────────────────────────
const uploadBox = document.getElementById('upload-box');

// Highlight box when a file is dragged over it
uploadBox.addEventListener('dragover', (e) => {
    e.preventDefault();  // Required to allow drop event
    uploadBox.style.background = '#eff6ff';
});

// Handle file dropped onto the upload box
uploadBox.addEventListener('drop', (e) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (file) {
        fileInput.files        = e.dataTransfer.files;
        fileNameEl.textContent = file.name;
        uploadBtn.disabled     = false;
    }
});


// ── STEP 2: Upload File and Get Suggested Mapping ─────────────
// Sends the file to the backend and shows the mapping table
uploadBtn.addEventListener('click', async () => {
    const file = fileInput.files[0];
    if (!file) return;

    // Show spinner while uploading
    statusBox.style.display      = 'block';
    statusContent.innerHTML      = `
        <div class="spinner"></div>
        <p>Uploading and detecting columns...</p>`;
    uploadBtn.disabled           = true;
    mappingSection.style.display = 'none';

    // Build multipart form data for file upload
    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch(`${API_BASE}/upload/`, {
            method: 'POST',
            body:   formData
        });

        const data = await response.json();

        if (response.ok) {
            // Store filename and mapping for Step 3
            uploadedFilename = data.filename;
            currentMapping   = data.suggested_mapping;

            // Show upload summary and mapping instructions
            statusContent.innerHTML = `
                <p class="status-success">
                    <i class="fas fa-check-circle"></i>
                    File uploaded! Please confirm the column mapping below.
                </p>
                <p>📁 Your columns:
                    <strong>${data.uploaded_columns.join(', ')}</strong>
                </p>
                ${data.missing_columns.length > 0
                    ? `<p style="color:#f59e0b">
                        ⚠️ Could not auto-detect:
                        <strong>${data.missing_columns.join(', ')}</strong>.
                        Please map them manually below.
                       </p>`
                    : `<p style="color:#10b981">
                        ✅ All columns detected successfully!
                       </p>`
                }
            `;

            // Build and show the mapping confirmation table
            buildMappingTable(data.suggested_mapping);
            mappingSection.style.display = 'block';

        } else {
            statusContent.innerHTML = `
                <p class="status-error">
                    <i class="fas fa-times-circle"></i>
                    Error: ${data.error}
                </p>`;
        }

    } catch (err) {
        statusContent.innerHTML = `
            <p class="status-error">
                <i class="fas fa-times-circle"></i>
                Could not connect to server. Make sure the backend is running.
            </p>`;
    }

    uploadBtn.disabled = false;
});


// ── Build Column Mapping Table ────────────────────────────────
// Creates a table row per uploaded column with a dropdown
// so the user can confirm or change the auto-detected match
function buildMappingTable(mapping) {
    mappingTable.innerHTML = `
        <table class="mapping-tbl">
            <thead>
                <tr>
                    <th>Your Column Name</th>
                    <th>Maps To (System Column)</th>
                </tr>
            </thead>
            <tbody>
                ${Object.entries(mapping).map(([col, mapped]) => `
                    <tr>
                        <td><strong>${col}</strong></td>
                        <td>
                            <select class="map-select" data-col="${col}">
                                <option value="">-- Skip this column --</option>
                                ${EXPECTED_COLUMNS.map(ec => `
                                    <option value="${ec}"
                                        ${mapped === ec ? 'selected' : ''}>
                                        ${ec}
                                    </option>
                                `).join('')}
                            </select>
                        </td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
}


// ── STEP 3: Confirm Mapping and Process Data ──────────────────
// Reads the user's dropdown selections and sends them to the
// backend to apply the mapping and save the cleaned data
document.getElementById('confirm-btn').addEventListener('click', async () => {

    // Read all dropdown selections into a mapping object
    const selects = document.querySelectorAll('.map-select');
    const mapping = {};
    selects.forEach(sel => {
        if (sel.value) mapping[sel.dataset.col] = sel.value;
    });

    // Show spinner while processing
    statusContent.innerHTML = `
        <div class="spinner"></div>
        <p>Processing and cleaning your data...</p>`;

    try {
        const response = await fetch(`${API_BASE}/upload/confirm`, {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify({
                filename: uploadedFilename,
                mapping:  mapping
            })
        });

        const data = await response.json();

        if (response.ok) {
            // Hide mapping table and show success with dashboard link
            mappingSection.style.display = 'none';
            statusContent.innerHTML = `
                <p class="status-success">
                    <i class="fas fa-check-circle"></i>
                    Data processed successfully!
                </p>
                <p>📊 <strong>${data.rows}</strong> records ready for analysis</p>
                <p>📁 Final columns: <strong>${data.columns.join(', ')}</strong></p>
                <br>
                <a href="dashboard.html" class="btn-primary">
                    <i class="fas fa-chart-bar"></i> View Dashboard
                </a>
            `;
        } else {
            statusContent.innerHTML = `
                <p class="status-error">Error: ${data.error}</p>`;
        }

    } catch (err) {
        statusContent.innerHTML = `
            <p class="status-error">Could not connect to server.</p>`;
    }
});