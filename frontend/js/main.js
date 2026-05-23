// ============================================================
// main.js — Upload Page with Flexible Column Mapping
// Handles file upload, displays auto-detected column mapping
// for user confirmation, then submits confirmed mapping
// to the backend to finalize data processing.
// ============================================================

const API_BASE = 'http://127.0.0.1:5000/api';

// Expected system columns for the dropdown options
const EXPECTED_COLUMNS = [
    'Customer_Name', 'Sex', 'Product', 'Category',
    'Quantity', 'Date', 'Unit_Price', 'Amount', 'Channel'
];

// Stores the uploaded filename and mapping state
let uploadedFilename = '';
let currentMapping   = {};

// ── DOM References ────────────────────────────────────────────
const fileInput      = document.getElementById('file-input');
const uploadBtn      = document.getElementById('upload-btn');
const fileNameEl     = document.getElementById('file-name');
const statusBox      = document.getElementById('status-box');
const statusContent  = document.getElementById('status-content');
const mappingSection = document.getElementById('mapping-section');
const mappingTable   = document.getElementById('mapping-table');


// ── File Selected ─────────────────────────────────────────────
fileInput.addEventListener('change', () => {
    const file = fileInput.files[0];
    if (file) {
        fileNameEl.textContent = file.name;
        uploadBtn.disabled     = false;
    }
});


// ── Drag and Drop ─────────────────────────────────────────────
const uploadBox = document.getElementById('upload-box');
uploadBox.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadBox.style.background = '#eff6ff';
});

uploadBox.addEventListener('drop', (e) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (file) {
        fileInput.files        = e.dataTransfer.files;
        fileNameEl.textContent = file.name;
        uploadBtn.disabled     = false;
    }
});


// ── Upload File and Get Column Mapping ────────────────────────
uploadBtn.addEventListener('click', async () => {
    const file = fileInput.files[0];
    if (!file) return;

    statusBox.style.display  = 'block';
    statusContent.innerHTML  = '<div class="spinner"></div><p>Uploading and detecting columns...</p>';
    uploadBtn.disabled       = true;
    mappingSection.style.display = 'none';

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch(`${API_BASE}/upload/`, {
            method: 'POST',
            body:   formData
        });

        const data = await response.json();

        if (response.ok) {
            uploadedFilename = data.filename;
            currentMapping   = data.suggested_mapping;

            // Show upload success summary
            statusContent.innerHTML = `
                <p class="status-success">
                    <i class="fas fa-check-circle"></i>
                    File uploaded! Now confirm your column mapping below.
                </p>
                <p>📁 Uploaded columns: <strong>${data.uploaded_columns.join(', ')}</strong></p>
                ${data.missing_columns.length > 0
                    ? `<p style="color:#f59e0b">
                        ⚠️ Could not auto-detect:
                        <strong>${data.missing_columns.join(', ')}</strong>.
                        Please map them manually below.
                       </p>`
                    : '<p style="color:#10b981">✅ All columns detected successfully!</p>'
                }
            `;

            // Build the mapping confirmation table
            buildMappingTable(data.suggested_mapping);
            mappingSection.style.display = 'block';

        } else {
            statusContent.innerHTML = `
                <p class="status-error">Error: ${data.error}</p>
            `;
        }
    } catch (err) {
        statusContent.innerHTML = `
            <p class="status-error">Could not connect to server.</p>
        `;
    }

    uploadBtn.disabled = false;
});


// ── Build Column Mapping Table ────────────────────────────────
// Creates a table row for each uploaded column with a dropdown
// so the user can confirm or change the auto-detected mapping
function buildMappingTable(mapping) {
    mappingTable.innerHTML = `
        <table class="mapping-tbl">
            <thead>
                <tr>
                    <th>Your Column</th>
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


// ── Confirm Mapping and Process Data ─────────────────────────
document.getElementById('confirm-btn').addEventListener('click', async () => {
    // Read current dropdown selections
    const selects = document.querySelectorAll('.map-select');
    const mapping = {};
    selects.forEach(sel => {
        if (sel.value) mapping[sel.dataset.col] = sel.value;
    });

    statusContent.innerHTML = '<div class="spinner"></div><p>Processing your data...</p>';

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
            mappingSection.style.display = 'none';
            statusContent.innerHTML = `
                <p class="status-success">
                    <i class="fas fa-check-circle"></i>
                    Data processed successfully!
                </p>
                <p>📊 <strong>${data.rows}</strong> records ready for analysis</p>
                <p>📁 Columns mapped: <strong>${data.columns.join(', ')}</strong></p>
                <br>
                <a href="dashboard.html" class="btn-primary">
                    <i class="fas fa-chart-bar"></i> View Dashboard
                </a>
            `;
        } else {
            statusContent.innerHTML = `
                <p class="status-error">Error: ${data.error}</p>
            `;
        }
    } catch (err) {
        statusContent.innerHTML = `
            <p class="status-error">Could not connect to server.</p>
        `;
    }
});