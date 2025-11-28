export async function exportMermaidAsPNG(elementId) {
  try {
    const element = document.getElementById(elementId)
    if (!element) {
      throw new Error('Mermaid element not found')
    }

    const svg = element.querySelector('svg')
    if (!svg) {
      throw new Error('SVG not found in mermaid element')
    }

    // Get SVG data
    const svgData = new XMLSerializer().serializeToString(svg)
    const canvas = document.createElement('canvas')
    const ctx = canvas.getContext('2d')
    
    const img = new Image()
    const svgBlob = new Blob([svgData], { type: 'image/svg+xml;charset=utf-8' })
    const url = URL.createObjectURL(svgBlob)

    return new Promise((resolve, reject) => {
      img.onload = () => {
        canvas.width = img.width
        canvas.height = img.height
        ctx.drawImage(img, 0, 0)
        
        canvas.toBlob(blob => {
          URL.revokeObjectURL(url)
          resolve(blob)
        })
      }
      img.onerror = reject
      img.src = url
    })
  } catch (error) {
    console.error('Export mermaid error:', error)
    throw error
  }
}

export function exportMermaidAsSVG(elementId) {
  const element = document.getElementById(elementId)
  if (!element) {
    throw new Error('Mermaid element not found')
  }

  const svg = element.querySelector('svg')
  if (!svg) {
    throw new Error('SVG not found')
  }

  const svgData = new XMLSerializer().serializeToString(svg)
  const blob = new Blob([svgData], { type: 'image/svg+xml;charset=utf-8' })
  
  return blob
}