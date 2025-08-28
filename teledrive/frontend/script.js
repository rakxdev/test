// DOM Elements
const uploadButton = document.getElementById('uploadButton');
const uploadModal = document.getElementById('uploadModal');
const previewModal = document.getElementById('previewModal');
const closeModalButtons = document.querySelectorAll('.close-modal');
const dropArea = document.getElementById('dropArea');
const fileInput = document.getElementById('fileInput');
const fileList = document.getElementById('fileList');
const cancelUpload = document.getElementById('cancelUpload');
const startUpload = document.getElementById('startUpload');
const fileCards = document.querySelectorAll('.file-card');
const previewContent = document.getElementById('previewContent');
const previewFileName = document.getElementById('previewFileName');

// Open upload modal
uploadButton.addEventListener('click', () => {
    uploadModal.classList.add('active');
});

// Close modals
closeModalButtons.forEach(button => {
    button.addEventListener('click', () => {
        uploadModal.classList.remove('active');
        previewModal.classList.remove('active');
    });
});

// Close modals when clicking outside
window.addEventListener('click', (e) => {
    if (e.target === uploadModal) {
        uploadModal.classList.remove('active');
    }
    if (e.target === previewModal) {
        previewModal.classList.remove('active');
    }
});

// Cancel upload
cancelUpload.addEventListener('click', () => {
    uploadModal.classList.remove('active');
    fileList.innerHTML = '';
});

// Browse files
dropArea.addEventListener('click', () => {
    fileInput.click();
});

// Handle file selection
fileInput.addEventListener('change', (e) => {
    handleFiles(e.target.files);
});

// Drag and drop functionality
['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    dropArea.addEventListener(eventName, preventDefaults, false);
});

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

['dragenter', 'dragover'].forEach(eventName => {
    dropArea.addEventListener(eventName, highlight, false);
});

['dragleave', 'drop'].forEach(eventName => {
    dropArea.addEventListener(eventName, unhighlight, false);
});

function highlight() {
    dropArea.style.borderColor = 'var(--primary)';
    dropArea.style.backgroundColor = 'rgba(108, 92, 231, 0.1)';
}

function unhighlight() {
    dropArea.style.borderColor = 'var(--border)';
    dropArea.style.backgroundColor = 'transparent';
}

dropArea.addEventListener('drop', handleDrop, false);

function handleDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;
    handleFiles(files);
}

function handleFiles(files) {
    fileList.innerHTML = '';
    [...files].forEach(file => {
        renderFileItem(file);
    });
}

function renderFileItem(file) {
    const fileItem = document.createElement('div');
    fileItem.className = 'file-item';

    const fileSize = formatFileSize(file.size);

    fileItem.innerHTML = `
        <i class="fas ${getFileIcon(file.type)}"></i>
        <div class="file-item-info">
            <div class="file-item-name">${file.name}</div>
            <div class="file-item-size">${fileSize}</div>
        </div>
        <div class="progress-container">
            <div class="progress-bar" id="progress-${file.name.replace(/\s+/g, '-')}"></div>
        </div>
    `;

    fileList.appendChild(fileItem);
}

function getFileIcon(fileType) {
    if (fileType.includes('image')) return 'fa-file-image';
    if (fileType.includes('pdf')) return 'fa-file-pdf';
    if (fileType.includes('audio')) return 'fa-file-audio';
    if (fileType.includes('video')) return 'fa-file-video';
    if (fileType.includes('zip') || fileType.includes('rar')) return 'fa-file-archive';
    return 'fa-file';
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Simulate file upload
startUpload.addEventListener('click', () => {
    const progressBars = document.querySelectorAll('.progress-bar');
    let progress = 0;

    const interval = setInterval(() => {
        progress += 5;
        progressBars.forEach(bar => {
            bar.style.width = `${progress}%`;
        });

        if (progress >= 100) {
            clearInterval(interval);
            setTimeout(() => {
                uploadModal.classList.remove('active');
                fileList.innerHTML = '';
                alert('Files uploaded successfully!');
            }, 500);
        }
    }, 100);
});

// File preview functionality
fileCards.forEach(card => {
    card.addEventListener('click', () => {
        const fileName = card.querySelector('.file-name').textContent;
        const fileType = card.getAttribute('data-type');

        previewFileName.textContent = fileName;

        // Render preview based on file type
        if (fileType === 'image') {
            previewContent.innerHTML = `<img src="https://images.unsplash.com/photo-1541701494587-cb58502866ab?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1170&q=80" alt="${fileName}" class="preview-image">`;
        } else if (fileType === 'pdf') {
            previewContent.innerHTML = `
                <div style="background: #f5f5f5; padding: 20px; border-radius: 10px; text-align: center;">
                    <i class="fas fa-file-pdf" style="font-size: 5rem; color: #d73535; margin-bottom: 20px;"></i>
                    <p>PDF Preview not available in demo</p>
                    <p>Click Download to view the file</p>
                </div>
            `;
        } else if (fileType === 'text') {
            previewContent.innerHTML = `
                <div class="preview-text">
# Project Notes

## Goals
- Complete initial design
- Implement core features
- Test with users

## Timeline
- Design phase: 2 weeks
- Implementation: 4 weeks
- Testing: 2 weeks

## Resources
- Design team: 2 members
- Development team: 4 members
- QA team: 2 members
                        </div>
                    `;
        } else {
            previewContent.innerHTML = `
                <div style="padding: 40px; text-align: center;">
                    <i class="fas ${getFileIcon(fileType)}" style="font-size: 5rem; color: var(--primary); margin-bottom: 20px;"></i>
                    <h3>${fileName}</h3>
                    <p>Preview not available for this file type</p>
                    <p>Click Download to access the file</p>
                </div>
            `;
        }

        previewModal.classList.add('active');
    });
});

// Simulate file download
document.querySelectorAll('.action-btn .fa-download').forEach(button => {
    button.parentElement.addEventListener('click', (e) => {
        e.stopPropagation();
        const fileName = e.target.closest('.file-card').querySelector('.file-name').textContent;
        alert(`Downloading ${fileName}...`);
    });
});

// Simulate file sharing
document.querySelectorAll('.action-btn .fa-share-alt').forEach(button => {
    button.parentElement.addEventListener('click', (e) => {
        e.stopPropagation();
        const fileName = e.target.closest('.file-card').querySelector('.file-name').textContent;
        alert(`Generating share link for ${fileName}...`);
    });
});
