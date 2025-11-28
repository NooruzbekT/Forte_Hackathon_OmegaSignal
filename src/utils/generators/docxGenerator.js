import { Document, Packer, Paragraph, HeadingLevel, TextRun, AlignmentType } from 'docx'
import { saveAs } from 'file-saver'

export async function generateDOCX(document) {
  const doc = new Document({
    sections: [{
      properties: {},
      children: [
        // Title
        new Paragraph({
          text: document.title,
          heading: HeadingLevel.HEADING_1,
          alignment: AlignmentType.CENTER,
          spacing: { after: 400 }
        }),

        // Metadata
        new Paragraph({
          children: [
            new TextRun({
              text: 'Тип документа: ',
              bold: true
            }),
            new TextRun(document.type)
          ],
          spacing: { after: 200 }
        }),

        new Paragraph({
          children: [
            new TextRun({
              text: 'Дата создания: ',
              bold: true
            }),
            new TextRun(new Date(document.createdAt).toLocaleDateString('ru-RU'))
          ],
          spacing: { after: 400 }
        }),

        // Executive Summary
        new Paragraph({
          text: 'Executive Summary',
          heading: HeadingLevel.HEADING_2,
          spacing: { after: 200 }
        }),

        new Paragraph({
          text: document.executiveSummary || 'N/A',
          spacing: { after: 400 }
        }),

        // Requirements
        new Paragraph({
          text: 'Requirements',
          heading: HeadingLevel.HEADING_2,
          spacing: { after: 200 }
        }),

        ...(document.requirements || []).map(req => 
          new Paragraph({
            text: `• ${req}`,
            spacing: { after: 100 },
            indent: { left: 720 }
          })
        ),

        // Quality Assessment
        new Paragraph({
          text: 'Quality Assessment',
          heading: HeadingLevel.HEADING_2,
          spacing: { before: 400, after: 200 }
        }),

        new Paragraph({
          children: [
            new TextRun({
              text: 'Overall Quality: ',
              bold: true
            }),
            new TextRun(`${Math.round((document.quality?.overall || 0) * 100)}%`)
          ],
          spacing: { after: 100 }
        }),

        new Paragraph({
          children: [
            new TextRun({
              text: 'Completeness: ',
              bold: true
            }),
            new TextRun(`${Math.round((document.quality?.completeness || 0) * 100)}%`)
          ],
          spacing: { after: 100 }
        }),

        new Paragraph({
          children: [
            new TextRun({
              text: 'Consistency: ',
              bold: true
            }),
            new TextRun(`${Math.round((document.quality?.consistency || 0) * 100)}%`)
          ]
        })
      ]
    }]
  })

  const blob = await Packer.toBlob(doc)
  saveAs(blob, `${document.title}.docx`)
}