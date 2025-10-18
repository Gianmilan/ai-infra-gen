/**
 * AI Infrastructure Generator - Frontend Application
 */

/**
 * Use an example by populating the requirements textarea
 * and optionally setting the generator type
 */
function useExample(element, type) {
    const exampleContent = element.querySelector('.example-content');
    document.getElementById('requirements').value = exampleContent.textContent.trim();

    if (type) {
        document.getElementById('generatorType').value = type;
    }
}

/**
 * Main generation function - calls the appropriate backend endpoint
 */
async function generate() {
    const requirements = document.getElementById('requirements').value;
    const generatorType = document.getElementById('generatorType').value;
    const btn = document.getElementById('generateBtn');
    const output = document.getElementById('output');
    const status = document.getElementById('status');
    const copyBtn = document.getElementById('copyBtn');
    const downloadBtn = document.getElementById('downloadBtn');
    const outputTitle = document.getElementById('outputTitle');

    if (!requirements.trim()) {
        status.className = 'status error';
        status.textContent = 'L Please describe your infrastructure needs';
        return;
    }

    // Update UI to loading state
    btn.disabled = true;
    btn.textContent = '� Generating...';
    output.value = '';
    status.className = 'status loading';
    status.textContent = 'AI is analyzing your requirements...';
    copyBtn.disabled = true;
    downloadBtn.disabled = true;

    try {
        // Choose endpoint based on selection
        const endpoint = `/generate/${generatorType}`;

        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({requirements})
        });

        const data = await response.json();

        if (data.error) {
            status.className = 'status error';
            status.textContent = 'L ' + data.error;
        } else {
            output.value = data.code;

            // Update title based on detected or selected type
            const finalType = data.detected_type || generatorType;
            if (finalType === 'kubernetes') {
                outputTitle.textContent = 'Generated Kubernetes Manifests';
            } else if (finalType === 'terraform') {
                outputTitle.textContent = '<Generated Terraform Code';
            } else {
                outputTitle.textContent = '� Generated Code';
            }

            // Build status message
            let statusText = 'Infrastructure code generated! ';
            if (data.detected_type) {
                statusText += `(Detected: ${data.detected_type}) `;
            }
            statusText += (data.validated ? '(Validated)' : '(Validation skipped)');

            if (data.cached) {
                statusText += ' =� (from cache)';
            }

            status.className = 'status success';
            status.textContent = statusText;

            copyBtn.disabled = false;
            downloadBtn.disabled = false;

            // Store the type for download
            output.dataset.generatorType = data.detected_type || generatorType;
        }
    } catch (error) {
        status.className = 'status error';
        status.textContent = 'L Error: ' + error.message;
    }

    btn.disabled = false;
    btn.textContent = '( Generate Infrastructure';
}

/**
 * Copy generated code to clipboard
 */
function copyCode() {
    const output = document.getElementById('output');
    output.select();
    document.execCommand('copy');

    const btn = document.getElementById('copyBtn');
    const oldText = btn.textContent;
    btn.textContent = 'Copied!';
    setTimeout(() => btn.textContent = oldText, 2000);
}

/**
 * Download generated code as a file
 */
function downloadCode() {
    const output = document.getElementById('output');
    const code = output.value;
    const generatorType = output.dataset.generatorType || 'terraform';

    // Choose filename based on type
    const filename = generatorType === 'kubernetes' ? 'manifests.yaml' : 'main.tf';

    const blob = new Blob([code], {type: 'text/plain'});
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
}

/**
 * Show cache information
 */
async function showCacheInfo() {
    const cacheInfo = document.getElementById('cacheInfo');

    try {
        const response = await fetch('/cache/info');
        const data = await response.json();

        const sizeKB = (data.total_bytes / 1024).toFixed(2);
        const sizeChars = data.total_chars.toLocaleString();

        cacheInfo.innerHTML = `
            <strong>Cache Status:</strong> ${data.enabled ? '✅ Enabled' : '❌ Disabled'}<br>
            <strong>Cached Items:</strong> ${data.items}<br>
            <strong>Total Size:</strong> ${sizeKB} KB (${sizeChars} chars)<br>
            <strong>Location:</strong> ${data.file_path}
        `;
        cacheInfo.style.display = 'block';
    } catch (error) {
        cacheInfo.innerHTML = `<span style="color: red;">Error: ${error.message}</span>`;
        cacheInfo.style.display = 'block';
    }
}

/**
 * Clear the cache
 */
async function clearCache() {
    if (!confirm('Are you sure you want to clear the cache? This will remove all cached responses.')) {
        return;
    }

    const cacheInfo = document.getElementById('cacheInfo');

    try {
        const response = await fetch('/cache/clear', {
            method: 'POST'
        });

        const data = await response.json();

        if (response.ok) {
            cacheInfo.innerHTML = `<span style="color: green;">✅ ${data.message}</span>`;
            cacheInfo.style.display = 'block';
            setTimeout(() => cacheInfo.style.display = 'none', 3000);
        } else {
            cacheInfo.innerHTML = `<span style="color: red;">❌ ${data.error}</span>`;
            cacheInfo.style.display = 'block';
        }
    } catch (error) {
        cacheInfo.innerHTML = `<span style="color: red;">❌ Error: ${error.message}</span>`;
        cacheInfo.style.display = 'block';
    }
}

/**
 * Initialize event listeners when DOM is ready
 */
document.addEventListener('DOMContentLoaded', () => {
    // Allow Ctrl/Cmd + Enter to generate
    document.getElementById('requirements').addEventListener('keydown', (e) => {
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            generate();
        }
    });
});
