# S3 Direct Upload Implementation

This implementation provides direct S3 upload functionality for video files in the SubChapter creation and update forms, eliminating the need for background tasks or Celery.

## Features

- **Upload on Form Submission**: Videos are uploaded to S3 only when the form is submitted, preventing orphaned files
- **Automatic Cleanup**: Orphaned S3 files are automatically cleaned up when users change selections or abandon forms
- **Progress Tracking**: Real-time upload progress with visual progress bar
- **No Background Tasks**: Eliminates the need for Celery or background task processing
- **Automatic URL Generation**: S3 URLs are automatically generated and stored in the database
- **Error Handling**: Comprehensive error handling for upload failures

## Implementation Details

### Backend Changes

1. **New API Endpoints**: 
   - `S3PresignedURLView` generates presigned URLs for direct S3 uploads
   - `S3CleanupView` deletes orphaned S3 files
   - URLs: `/api/s3-presigned-url/`, `/api/s3-cleanup/`

2. **Updated Views**: 
   - `SubChapterCreatView` and `SubChapterUpdateView` now handle S3 URLs instead of file uploads
   - S3 settings are passed to templates for frontend use

3. **URL Configuration**: Added new URL patterns for the S3 API endpoints

### Frontend Changes

1. **Create Template** (`create_sub_chapter.html`):
   - Custom upload button with file selection
   - Progress bar for upload tracking
   - Hidden input field for S3 video URL
   - JavaScript for upload-on-submit and cleanup functionality

2. **Update Template** (`update_sub_chapter.html`):
   - Similar changes as create template
   - Preserves existing video if no new upload is provided

### JavaScript Functionality

- **File Selection**: Custom button triggers file selection
- **Upload on Submit**: Video uploads only when form is submitted
- **Automatic Cleanup**: Previous uploads are cleaned up when user changes selection
- **Page Leave Cleanup**: Orphaned files are cleaned up when user leaves page
- **S3 URL Generation**: AJAX call to get presigned URL
- **Direct Upload**: XMLHttpRequest for direct S3 upload with progress tracking
- **Form Validation**: Ensures video is uploaded before form submission
- **Error Handling**: Comprehensive error messages and visual feedback

## Upload Flow

1. **User selects video file** → File is stored temporarily in browser
2. **User fills form fields** → No upload happens yet
3. **User clicks submit** → Video uploads to S3 with progress tracking
4. **Upload completes** → Form submits with S3 URL
5. **Cleanup on change** → If user changes video selection, old upload is cleaned up
6. **Cleanup on page leave** → If user leaves page without submitting, upload is cleaned up

## Configuration Requirements

### Production Environment
- AWS S3 bucket configured
- AWS credentials set in environment variables:
  - `AWS_ACCESS_KEY_ID`
  - `AWS_SECRET_ACCESS_KEY`
  - `AWS_STORAGE_BUCKET_NAME`
  - `AWS_S3_REGION_NAME`

### Development Environment
- S3 upload is disabled in development mode
- Files are handled through local storage

## Usage

1. **Create SubChapter**:
   - Navigate to SubChapter creation form
   - Click "Choose Video File" button
   - Select video file (shows file info but doesn't upload yet)
   - Fill other form fields
   - Click submit → Video uploads to S3, then form submits

2. **Update SubChapter**:
   - Navigate to SubChapter update form
   - Current video is displayed if exists
   - Click "Choose New Video File" to select new video
   - Leave empty to keep existing video
   - Submit form to save changes

## Benefits

- **No Orphaned Files**: Upload only happens on form submission
- **Automatic Cleanup**: Prevents S3 storage waste
- **Performance**: No server-side file processing
- **Scalability**: Direct upload reduces server load
- **Reliability**: S3 handles large file uploads efficiently
- **User Experience**: Real-time progress feedback
- **Cost Effective**: Reduces server bandwidth usage and S3 storage waste

## Error Handling

- Network errors during upload
- Invalid file types
- File size limits
- S3 configuration issues
- Presigned URL expiration
- Cleanup failures (logged but don't block user)

## Security

- CSRF protection for API calls
- Presigned URLs expire after 1 hour
- File type validation on frontend and backend
- Unique file names to prevent conflicts
- Automatic cleanup prevents storage abuse

## Cleanup Scenarios

1. **User changes video selection**: Previous upload is automatically deleted
2. **User leaves page without submitting**: Upload is cleaned up
3. **Form submission fails**: Upload remains (will be used by successful submission)
4. **Network errors**: Failed uploads don't create orphaned files 