export function validateFileType(file, allowedTypes) {
  return allowedTypes.includes(file.type)
}

export function validateFileSize(file, maxSizeInMB) {
  const maxSizeInBytes = maxSizeInMB * 1024 * 1024
  return file.size <= maxSizeInBytes
}

export function validateImageFile(file) {
  const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
  return validateFileType(file, allowedTypes)
}

export function validateDocumentFile(file) {
  const allowedTypes = [
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
  ]
  return validateFileType(file, allowedTypes)
}