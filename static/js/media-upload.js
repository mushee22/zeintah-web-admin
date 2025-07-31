/**
 * Media Upload JavaScript
 * Handles video upload to S3 with progress tracking
 */

class MediaUploader {
    constructor() {
        this.uploadArea = document.getElementById('upload-area');
        this.fileInput = document.getElementById('file-input');
        this.browseBtn = document.getElementById('browse-btn');
        this.submitBtn = document.getElementById('submit-btn');
        this.progressContainer = document.getElementById('progress-container');
        this.progressFill = document.getElementById('progress-fill');
        this.progressText = document.getElementById('progress-text');
        this.alertContainer = document.getElementById('alert-container');
        this.filesList = document.getElementById('files-list');
        this.titleInput = document.getElementById('title');
        
        this.selectedFile = null;
        this.maxFileSize = 500 * 1024 * 1024; // 500MB
        this.allowedTypes = ['video/mp4', 'video/avi', 'video/mov', 'video/wmv', 'video/flv', 'video/webm'];
        
        this.init();
    }
    
    init() {
        this.attachEventListeners();
        this.loadUploadedFiles();
    }
    
    attachEventListeners() {
        // Browse button click
        this.browseBtn.addEventListener('click', () => this.fileInput.click());
        
        // File input change
        this.fileInput.addEventListener('change', (e) => this.handleFileSelect(e.target.files[0]));
        
        // Drag and drop events
        this.uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            this.uploadArea.classList.add('dragover');
        });
        
        this.uploadArea.addEventListener('dragleave', (e) => {
            e.preventDefault();
            this.uploadArea.classList.remove('dragover');
        });
        
        this.uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            this.uploadArea.classList.remove('dragover');
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                this.handleFileSelect(files[0]);
            }
        });
        
        // Form submission
        document.getElementById('upload-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.validateAndUpload();
        });
    }
    
    handleFileSelect(file) {
        if (!file) return;
        
        // Validate file type
        if (!this.allowedTypes.includes(file.type)) {
            this.showAlert('Please select a valid video file.', 'error');
            return;
        }
        
        // Validate file size
        if (file.size > this.maxFileSize) {
            this.showAlert('File size too large. Maximum size is 500MB.', 'error');
            return;
        }
        
        this.selectedFile = file;
        this.submitBtn.disabled = false;
        
        // Update upload area
        this.uploadArea.innerHTML = `
            <div class="upload-icon">✅</div>
            <h4>File Selected</h4>
            <p><strong>${file.name}</strong></p>
            <p>Size: ${this.formatFileSize(file.size)}</p>
            <button type="button" class="upload-btn" id="change-file-btn">Change File</button>
        `;
        
        // Add change file button event
        document.getElementById('change-file-btn').addEventListener('click', () => {
            this.fileInput.click();
        });
    }
    
    validateAndUpload() {
        if (!this.selectedFile) {
            this.showAlert('Please select a file to upload.', 'error');
            return;
        }
        
        if (!this.titleInput.value.trim()) {
            this.showAlert('Please enter a title for the video.', 'error');
            return;
        }
        
        this.uploadFile();
    }
    
    uploadFile() {
        const formData = new FormData();
        formData.append('file', this.selectedFile);
        formData.append('title', this.titleInput.value.trim());
        
        // Show progress
        this.progressContainer.style.display = 'block';
        this.submitBtn.disabled = true;
        
        // Create XMLHttpRequest for progress tracking
        const xhr = new XMLHttpRequest();
        
        xhr.upload.addEventListener('progress', (e) => {
            if (e.lengthComputable) {
                const percentComplete = (e.loaded / e.total) * 100;
                this.progressFill.style.width = percentComplete + '%';
                this.progressText.textContent = Math.round(percentComplete) + '%';
            }
        });
        
        xhr.addEventListener('load', () => {
            if (xhr.status === 201) {
                const response = JSON.parse(xhr.responseText);
                this.showAlert('Video uploaded successfully!', 'success');
                this.resetForm();
                this.loadUploadedFiles();
            } else {
                const response = JSON.parse(xhr.responseText);
                this.showAlert(response.message || 'Upload failed. Please try again.', 'error');
            }
            this.progressContainer.style.display = 'none';
            this.submitBtn.disabled = false;
        });
        
        xhr.addEventListener('error', () => {
            this.showAlert('Upload failed. Please check your connection and try again.', 'error');
            this.progressContainer.style.display = 'none';
            this.submitBtn.disabled = false;
        });
        
        xhr.open('POST', '/web/media/upload/');
        
        // Add CSRF token
        const csrfToken = this.getCookie('csrftoken');
        if (csrfToken) {
            xhr.setRequestHeader('X-CSRFToken', csrfToken);
        }
        
        xhr.send(formData);
    }
    
    resetForm() {
        this.selectedFile = null;
        this.titleInput.value = '';
        this.fileInput.value = '';
        this.submitBtn.disabled = true;
        this.uploadArea.innerHTML = `
            <div class="upload-icon">📁</div>
            <h4>Drag & Drop your video here</h4>
            <p>or</p>
            <button type="button" class="upload-btn" id="browse-btn">Browse Files</button>
        `;
        
        // Reattach browse button event
        document.getElementById('browse-btn').addEventListener('click', () => {
            this.fileInput.click();
        });
    }
    
    loadUploadedFiles() {
        fetch('/api/media/upload/')
            .then(response => response.json())
            .then(data => {
                if (data.resp_code === 1) {
                    this.displayFiles(data.data);
                }
            })
            .catch(error => {
                console.error('Error loading files:', error);
            });
    }
    
    displayFiles(files) {
        if (files.length === 0) {
            this.filesList.innerHTML = '<p>No videos uploaded yet.</p>';
            return;
        }
        
        this.filesList.innerHTML = files.map(file => `
            <div class="file-item">
                <div class="upload-icon">🎥</div>
                <div class="file-info">
                    <div class="file-name">${file.title}</div>
                    <div class="file-size">${this.formatFileSize(file.file_size)} • ${file.file_type}</div>
                    <a href="${file.file_url}" target="_blank" class="file-url">View Video</a>
                </div>
            </div>
        `).join('');
    }
    
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    showAlert(message, type) {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type}`;
        alertDiv.textContent = message;
        
        this.alertContainer.innerHTML = '';
        this.alertContainer.appendChild(alertDiv);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            alertDiv.remove();
        }, 5000);
    }
    
    getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    new MediaUploader();
}); 