export function parseMarkdown(text) {
  return text
    // Headers
    .replace(/^### (.*$)/gim, '<h3>$1</h3>')
    .replace(/^## (.*$)/gim, '<h2>$1</h2>')
    .replace(/^# (.*$)/gim, '<h1>$1</h1>')
    // Bold
    .replace(/\*\*(.*)\*\*/gim, '<strong>$1</strong>')
    // Italic
    .replace(/\*(.*)\*/gim, '<em>$1</em>')
    // Links
    .replace(/\[(.*?)\]\((.*?)\)/gim, '<a href="$2">$1</a>')
    // Line breaks
    .replace(/\n/gim, '<br>')
}

export function extractMermaidCode(text) {
  const regex = /```mermaid\n([\s\S]*?)\n```/g
  const matches = []
  let match

  while ((match = regex.exec(text)) !== null) {
    matches.push(match[1])
  }

  return matches
}

export function removeMermaidBlocks(text) {
  return text.replace(/```mermaid\n[\s\S]*?\n```/g, '')
}