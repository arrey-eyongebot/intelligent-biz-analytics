// ============================================================
// main.js — Smart Upload & Column Mapping Logic
//
// FLOW:
// 1. User selects a CSV or Excel file
// 2. File is uploaded to the backend
// 3. If columns match perfectly → go straight to dashboard
// 4. If columns don't match → show mapping table where:
//    LEFT  = required system column name
//    RIGHT = dropdown of columns from the uploaded file
// 5. User confirms mapping → data saved → go to dashboard
// Unmatched columns are automatically dropped.
// ============================================================

const API_BASE = 'http://127.0.0.1:5000/api';

// Required system columns (must all be mapped)
const REQUIRED_COLUMNS = [
    'Product', 'Category', 'Quantity',
    'Date', 'Unit_Price', 'Amount', 'Channel'
];

// Optional system columns (mapped if available)
const OPTIONAL_COLUMNS = ['Customer_Name', 'Sex'];

// State variables
let uploadedFilename  = '';
let uploadedColumns   = [];

// ── DOM References ────────────────────────────────────────────
const fileInput      = document.getElementById('file-input');
const uploadBtn      = document.getElementById('upload-btn');
const fileNameEl     = document.getElementById('file-name');
const statusBox      = document.getElementById('status-box');
const statusContent  = document.getElementById('status-content');
const mappingSection = document.getElementById('mapping-section');
const mappingTable   = document.getElementById('mapping-table');


// ── File Selected via Browse ──────────────────────────────────
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


// ── Upload Button Clicked ─────────────────────────────────────
uploadBtn.addEventListener('click', async (e) => {
    e.preventDefault();
    e.stopPropagation();

    const file = fileInput.files[0];
    if (!file) return;

    // Show loading spinner
    statusBox.style.display      = 'block';
    statusContent.innerHTML      = `
        <div class="spinner"></div>
        <p>Uploading and checking columns...</p>`;
    uploadBtn.disabled           = true;
    mappingSection.style.display = 'none';

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch(`${API_BASE}/upload/`, {
            method:      'POST',
            body:        formData,
            credentials: 'include'
        });

        const data = await response.json();

        if (!response.ok) {
            statusContent.innerHTML = `
                <p class="status-error">
                    <i class="fas fa-times-circle"></i>
                    Error: ${data.error}
                </p>`;
            uploadBtn.disabled = false;
            return;
        }

        if (data.perfect_match) {
            // ── Perfect Match: go straight to dashboard ───────
            statusContent.innerHTML = `
                <p class="status-success">
                    <i class="fas fa-check-circle"></i>
                    All columns matched perfectly!
                    ${data.rows} records loaded.
                </p>
                <p>Redirecting to dashboard...</p>
            `;
            setTimeout(() => {
                window.location.href = 'dashboard.html';
            }, 1500);

        } else {
            // ── Columns don't match: show mapping table ───────
            uploadedFilename = data.filename;
            uploadedColumns  = data.uploaded_columns;

            statusContent.innerHTML = `
                <p style="color:#f59e0b">
                    <i class="fas fa-exclamation-triangle"></i>
                    <strong>Column mismatch detected.</strong>
                    Please map your columns below.
                </p>
                <p>Missing required columns:
                    <strong>${data.missing_columns.join(', ')}</strong>
                </p>
            `;

            // Build and show the mapping table
            buildMappingTable(data.uploaded_columns);
            mappingSection.style.display = 'block';

            // Scroll down to mapping table
            setTimeout(() => {
                mappingSection.scrollIntoView({ behavior: 'smooth' });
            }, 300);
        }

    } catch (err) {
        statusContent.innerHTML = `
            <p class="status-error">
                <i class="fas fa-times-circle"></i>
                Could not connect to server.
                Make sure the backend is running.
            </p>`;
    }

    uploadBtn.disabled = false;
});


// ── Build Mapping Table ───────────────────────────────────────
// LEFT  = required/optional system column name
// RIGHT = dropdown of columns from the uploaded file
function buildMappingTable(uploadedCols) {
    // Build dropdown options from uploaded file columns
    const options = `
        <option value="">-- Not in my file --</option>
        ${uploadedCols.map(col => `
            <option value="${col}">${col}</option>
        `).join('')}
    `;

    // Try to auto-suggest a match for each system column
    // by checking if names are similar
    function autoSuggest(systemCol) {
        const lower = systemCol.toLowerCase().replace('_', '');
        const match = uploadedCols.find(c =>
            c.toLowerCase().replace(/[^a-z]/g, '') === lower ||
            c.toLowerCase().includes(lower) ||
            lower.includes(c.toLowerCase())
        );
        return match || '';
    }

    mappingTable.innerHTML = `
        <table class="mapping-tbl">
            <thead>
                <tr>
                    <th>System Column (Required)</th>
                    <th>Your File Column</th>
                </tr>
            </thead>
            <tbody>
                <!-- Required columns -->
                ${REQUIRED_COLUMNS.map(col => {
                    const suggested = autoSuggest(col);
                    return `
                    <tr>
                        <td>
                            <strong>${col}</strong>
                            <span class="required"> *</span>
                        </td>
                        <td>
                            <select class="map-select" data-system="${col}">
                                ${uploadedCols.map(uc => `
                                    <option value="${uc}"
                                        ${uc === suggested ? 'selected' : ''}>
                                        ${uc}
                                    </option>
                                `).join('')}
                                <option value=""
                                    ${!suggested ? 'selected' : ''}>
                                    -- Not in my file --
                                </option>
                            </select>
                        </td>
                    </tr>`;
                }).join('')}

                <!-- Divider for optional columns -->
                <tr>
                    <td colspan="2"
                        style="background:#f1f5f9;
                               color:#64748b;
                               font-size:0.85rem;
                               padding:0.5rem 1rem">
                        Optional Columns (select if available in your file)
                    </td>
                </tr>

                <!-- Optional columns -->
                ${OPTIONAL_COLUMNS.map(col => {
                    const suggested = autoSuggest(col);
                    return `
                    <tr>
                        <td>
                            <strong>${col}</strong>
                            <span style="color:#64748b;
                                         font-size:0.8rem">
                                (optional)
                            </span>
                        </td>
                        <td>
                            <select class="map-select" data-system="${col}">
                                <option value="">-- Not in my file --</option>
                                ${uploadedCols.map(uc => `
                                    <option value="${uc}"
                                        ${uc === suggested ? 'selected' : ''}>
                                        ${uc}
                                    </option>
                                `).join('')}
                            </select>
                        </td>
                    </tr>`;
                }).join('')}
            </tbody>
        </table>
        <p style="color:#64748b; font-size:0.85rem; margin-top:0.5rem">
            <i class="fas fa-info-circle"></i>
            Any columns in your file not mapped here will be dropped.
        </p>
    `;
}


// ── Confirm Mapping Button ────────────────────────────────────
document.getElementById('confirm-btn').addEventListener('click', async (e) => {
    e.preventDefault();
    e.stopPropagation();

    // Read all dropdown selections
    const selects = document.querySelectorAll('.map-select');
    const mapping = {};

    selects.forEach(sel => {
        const systemCol     = sel.dataset.system;
        const uploadedCol   = sel.value;
        if (uploadedCol) {
            mapping[systemCol] = uploadedCol;
        }
    });

    // Validate all required columns are mapped
    const unmapped = REQUIRED_COLUMNS.filter(col => !mapping[col]);
    if (unmapped.length > 0) {
        statusContent.innerHTML = `
            <p class="status-error">
                <i class="fas fa-times-circle"></i>
                Please map these required columns:
                <strong>${unmapped.join(', ')}</strong>
            </p>`;
        statusBox.style.display = 'block';
        return;
    }

    // Show processing spinner
    statusContent.innerHTML = `
        <div class="spinner"></div>
        <p>Processing and cleaning your data...</p>`;
    statusBox.style.display = 'block';

    try {
        const response = await fetch(`${API_BASE}/upload/confirm`, {
            method:      'POST',
            headers:     { 'Content-Type': 'application/json' },
            credentials: 'include',
            body:        JSON.stringify({
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
                    ${data.rows} records ready.
                </p>
                <p>Redirecting to dashboard...</p>
            `;
            // Redirect to dashboard after short delay
            setTimeout(() => {
                window.location.href = 'dashboard.html';
            }, 1500);

        } else {
            statusContent.innerHTML = `
                <p class="status-error">
                    <i class="fas fa-times-circle"></i>
                    ${data.error}
                </p>`;
        }

    } catch (err) {
        statusContent.innerHTML = `
            <p class="status-error">Could not connect to server.</p>`;
    }
});