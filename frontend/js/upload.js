const MAX_SIZE = 5 * 1024 * 1024; // 5Mb
const ALLOWED_TYPES = ['image/jpeg', 'image/png', 'image/gif'];

let currentUrl = "";

async function copyURLtoClipboard() {
    
    // const urlLabel = document.getElementById("currentUploadLabel");
    // copyToClipboard(urlLabel.textContent);
    try {
        await navigator.clipboard.writeText(currentUrl);
        showStatus('URL copied', 'success');
        
        const btn = document.getElementById('copyButton');
        const oldText = btn.textContent;
        btn.textContent = 'Copied';
        setTimeout(() => btn.textContent = oldText, 2000);
    } catch (error) {
        showStatus("Failed to copy URL", "error")
    }
}

async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        console.log('Текст успешно скопирован!');
    } catch (err) {
        console.error('Не удалось скопировать текст: ', err);
    }
}

function showStatus(message, type) {
    const status = document.getElementById("uploadStatus");
    if (!status) return;

    status.textContent = message;
    status.className = `upload-status-${type}`;
    status.style.display = 'block';

    if (type === "success") {
        setTimeout(() => {status.style.display = 'none'}, 5000);
    }
}

function validateFile(file) {
    if (!ALLOWED_TYPES.includes(file.type)) {
        showStatus('Only .jpg, .png and .gif files!', 'error');
        return false;
    }
    if (file.size > MAX_SIZE) {
        showStatus('File too large! Maximum file size is 5MB.', 'error');
        return false;
    }
    return true;
}

async function handleFile(file) {
    if (!file || !validateFile(file)) return;

    showStatus('Uploading...', 'info');

    try {
        const base64 = await fileToBase64(file);
        const success = saveImage(file.name, file.name, base64, file.size);
        url = file.name;

        if (success) {
            showStatus('Upload successful!', 'success');
            
            const urlLabel = document.getElementById("currentUploadLabel");
            if (urlLabel) {
                urlLabel.textContent = cutLongName(url, 50);
                urlLabel.title = url;
                currentUrl = url;
            }
            document.getElementById("fileInput").value = "";
        } else {
            showStatus("Upload failed. Please try again.", "error");
        }
    }
    catch (error) {
        showStatus("Upload failed " + error.message, "error");
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const dropArea = document.getElementById('dropArea');
    const fileInput = document.getElementById('fileInput');
    const browseButton = document.querySelector('.browse-file-button');
    const copyButton = document.getElementById('copyButton');

    dropArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropArea.classList.add('dragover');
    })

    dropArea.addEventListener('dragleave', (e) => {
        e.preventDefault();
        dropArea.classList.remove('dragover');
    })

    dropArea.addEventListener('drop', (e) => {
        e.preventDefault();
        dropArea.classList.add('dragover');
        if (e.dataTransfer.files[0]) {
            handleFile(e.dataTransfer.files[0]);
        }
        dropArea.classList.remove('dragover');
    })

    dropArea.addEventListener('click', () => fileInput.click());

    fileInput.addEventListener('change', (e) => {
        if (e.target.files[0]) {
            handleFile(e.target.files[0]);
        }
        // dropArea.classList.remove('dragover');
    })

    browseButton.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        fileInput.click();
    })
})