import jsPDF from 'jspdf'

export function generatePDF(document) {
  const doc = new jsPDF()
  let yPosition = 20

  // Helper function to add text with wrapping
  function addText(text, fontSize = 11, isBold = false) {
    doc.setFontSize(fontSize)
    doc.setFont('helvetica', isBold ? 'bold' : 'normal')
    
    const lines = doc.splitTextToSize(text, 170)
    lines.forEach(line => {
      if (yPosition > 280) {
        doc.addPage()
        yPosition = 20
      }
      doc.text(line, 20, yPosition)
      yPosition += fontSize * 0.5
    })
    yPosition += 5
  }

  // Title
  addText(document.title, 20, true)
  yPosition += 5

  // Metadata
  addText(`Тип документа: ${document.type}`, 11, true)
  addText(`Дата создания: ${new Date(document.createdAt).toLocaleDateString('ru-RU')}`)
  yPosition += 10

  // Executive Summary
  addText('Executive Summary', 14, true)
  addText(document.executiveSummary || 'N/A')
  yPosition += 10

  // Requirements
  addText('Requirements', 14, true)
  if (document.requirements && document.requirements.length > 0) {
    document.requirements.forEach(req => {
      addText(`• ${req}`)
    })
  } else {
    addText('No requirements specified')
  }
  yPosition += 10

  // Quality Assessment
  addText('Quality Assessment', 14, true)
  if (document.quality) {
    addText(`Overall Quality: ${Math.round(document.quality.overall * 100)}%`)
    addText(`Completeness: ${Math.round(document.quality.completeness * 100)}%`)
    addText(`Consistency: ${Math.round(document.quality.consistency * 100)}%`)
  }

  // Save
  doc.save(`${document.title}.pdf`)
}