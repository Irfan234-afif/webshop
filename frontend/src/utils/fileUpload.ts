/**
 * File upload utilities for Frappe backend
 */

export interface UploadFileResponse {
  message: {
    file_url: string
    file_name: string
    name: string
  }
}

export interface UploadProgress {
  loaded: number
  total: number
  percentage: number
}

/**
 * Upload a file to Frappe backend
 *
 * @param file File to upload
 * @param onProgress Optional callback for upload progress
 * @returns Promise with file URL and metadata
 */
export async function uploadFile(
  file: File,
  onProgress?: (progress: UploadProgress) => void
): Promise<UploadFileResponse['message']> {
  return new Promise((resolve, reject) => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('is_private', '0') // Make file public
    formData.append('folder', 'Home/Attachments') // Store in Attachments folder

    const xhr = new XMLHttpRequest()

    // Track upload progress
    if (onProgress) {
      xhr.upload.addEventListener('progress', (e) => {
        if (e.lengthComputable) {
          const percentage = Math.round((e.loaded / e.total) * 100)
          onProgress({
            loaded: e.loaded,
            total: e.total,
            percentage
          })
        }
      })
    }

    // Handle successful upload
    xhr.addEventListener('load', () => {
      if (xhr.status === 200) {
        try {
          const response: UploadFileResponse = JSON.parse(xhr.responseText)
          resolve(response.message)
        } catch (error) {
          reject(new Error('Failed to parse upload response'))
        }
      } else {
        reject(new Error(`Upload failed with status ${xhr.status}`))
      }
    })

    // Handle errors
    xhr.addEventListener('error', () => {
      reject(new Error('Upload failed due to network error'))
    })

    xhr.addEventListener('abort', () => {
      reject(new Error('Upload was cancelled'))
    })

    // Send request to Frappe upload endpoint
    xhr.open('POST', '/api/method/upload_file')
    xhr.send(formData)
  })
}

/**
 * Validate file before upload
 *
 * @param file File to validate
 * @param maxSizeMB Maximum file size in MB (default: 5)
 * @param allowedTypes Allowed MIME types (default: images and PDFs)
 * @returns Error message if invalid, null if valid
 */
export function validateFile(
  file: File,
  maxSizeMB: number = 5,
  allowedTypes: string[] = ['image/jpeg', 'image/png', 'image/jpg', 'application/pdf']
): string | null {
  // Check file size
  const maxSizeBytes = maxSizeMB * 1024 * 1024
  if (file.size > maxSizeBytes) {
    return `File size exceeds ${maxSizeMB}MB limit`
  }

  // Check file type
  if (!allowedTypes.includes(file.type)) {
    const allowedExtensions = allowedTypes
      .map(type => type.split('/')[1])
      .join(', ')
    return `File type not allowed. Allowed types: ${allowedExtensions}`
  }

  return null
}

/**
 * Format file size in human-readable format
 *
 * @param bytes File size in bytes
 * @returns Formatted file size (e.g., "2.5 MB")
 */
export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 Bytes'

  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))

  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`
}
