export const API_ENDPOINTS = {
  // Root & Health
  ROOT: '/',
  HEALTH: '/health',
  
  // Chat
  CHAT: '/api/chat',
  
  // Session Management
  SESSION_INFO: (sessionId) => `/api/session/${sessionId}`,
  SESSION_RESET: (sessionId) => `/api/session/${sessionId}/reset`,
  SESSION_SUMMARY: (sessionId) => `/api/session/${sessionId}/summary`,
  SESSION_DOCUMENT: (sessionId) => `/api/session/${sessionId}/document`,
  SESSION_UPLOAD_DOC: (sessionId) => `/api/session/${sessionId}/upload-doc`,
  SESSION_REPUBLISH: (sessionId) => `/api/session/${sessionId}/republish`,

  
  // Documents
  DOCUMENTS_LIST: '/api/documents',
  DOCUMENT_DOWNLOAD: (filename) => `/api/documents/${filename}`,
  DOCUMENT_DELETE: (filename) => `/api/documents/${filename}`,
  DOCUMENT_PUBLISH: (filename) => `/api/documents/${filename}/publish`,
  
  // Diagrams
  DIAGRAM_GENERATE: '/api/diagrams/generate',
  DIAGRAM_MERMAID_TO_PNG: '/api/diagrams/mermaid-to-png',
  
  // History
  HISTORY_LIST: '/api/history',
  HISTORY_GET: (sessionId) => `/api/history/${sessionId}`,
  HISTORY_DELETE: (sessionId) => `/api/history/${sessionId}`,
  
  // Statistics
  STATISTICS: '/api/statistics',
  
  // Confluence
  CONFLUENCE_PUBLISH: '/api/confluence/publish',
  
  // Assistant
  ASSISTANT_SUMMARY: '/api/assistant/summary',
  
  // Admin
  ADMIN_SESSIONS: '/api/admin/sessions',
  ADMIN_CLEANUP: '/api/admin/cleanup',
  ADMIN_CLEANUP_HISTORY: '/api/admin/cleanup-history'
}