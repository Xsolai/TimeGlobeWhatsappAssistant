import { PDFDocument, StandardFonts, rgb } from 'pdf-lib';

export interface PdfGenerationOptions {
  title: string;
  content: string;
  companyInfo?: {
    name: string;
    address: string;
  };
  signatureImage?: string;
  date?: Date;
}

const pdfService = {
  generateContractPDF: async (options: PdfGenerationOptions): Promise<Uint8Array> => {
    try {
      // Create a new PDF document
      const pdfDoc = await PDFDocument.create();
      
      // Embed the Helvetica font
      const helveticaFont = await pdfDoc.embedFont(StandardFonts.Helvetica);
      const helveticaBold = await pdfDoc.embedFont(StandardFonts.HelveticaBold);
      
      // Add a page
      const page = pdfDoc.addPage([595, 842]); // A4 size
      const { width, height } = page.getSize();
      
      let yPosition = height - 50;
      const margin = 50;
      const lineHeight = 15;
      const maxWidth = width - 2 * margin;
      
      // Add company logo placeholder
      page.drawText('TimeGlobe', {
        x: margin,
        y: yPosition,
        size: 24,
        font: helveticaBold,
        color: rgb(0.1, 0.4, 0.82), // #1967D2
      });
      
      yPosition -= 40;
      
      // Add title
      page.drawText(options.title, {
        x: margin,
        y: yPosition,
        size: 18,
        font: helveticaBold,
        color: rgb(0, 0, 0),
      });
      
      yPosition -= 30;
      
      // Add date
      const dateStr = (options.date || new Date()).toLocaleDateString('de-DE', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      });
      page.drawText(`Datum: ${dateStr}`, {
        x: margin,
        y: yPosition,
        size: 10,
        font: helveticaFont,
        color: rgb(0.4, 0.4, 0.4),
      });
      
      yPosition -= 30;
      
      // Add content
      const lines = options.content.split('\n');
      for (const line of lines) {
        if (yPosition < 100) {
          // Add new page if needed
          const newPage = pdfDoc.addPage([595, 842]);
          yPosition = height - 50;
          
          // Continue on new page
          newPage.drawText(line, {
            x: margin,
            y: yPosition,
            size: 11,
            font: helveticaFont,
            color: rgb(0, 0, 0),
            maxWidth: maxWidth,
          });
        } else {
          page.drawText(line, {
            x: margin,
            y: yPosition,
            size: 11,
            font: helveticaFont,
            color: rgb(0, 0, 0),
            maxWidth: maxWidth,
          });
        }
        
        yPosition -= lineHeight;
        
        // Add extra space for paragraphs
        if (line === '') {
          yPosition -= 10;
        }
      }
      
      // Add signature area if provided
      if (options.signatureImage) {
        yPosition -= 50;
        
        page.drawText('Unterschrift:', {
          x: margin,
          y: yPosition,
          size: 11,
          font: helveticaBold,
          color: rgb(0, 0, 0),
        });
        
        yPosition -= 10;
        
        // Add signature line
        page.drawLine({
          start: { x: margin, y: yPosition },
          end: { x: margin + 200, y: yPosition },
          thickness: 1,
          color: rgb(0, 0, 0),
        });
        
        // TODO: Add actual signature image
        // const signatureImageBytes = await fetch(options.signatureImage).then(res => res.arrayBuffer());
        // const signatureImage = await pdfDoc.embedPng(signatureImageBytes);
        // page.drawImage(signatureImage, {
        //   x: margin,
        //   y: yPosition - 60,
        //   width: 150,
        //   height: 50,
        // });
      }
      
      // Add footer
      const footerY = 30;
      page.drawText('EcomTask UG (haftungsbeschränkt) | Rauenthaler Straße 12 | 65197 Wiesbaden', {
        x: margin,
        y: footerY,
        size: 8,
        font: helveticaFont,
        color: rgb(0.5, 0.5, 0.5),
      });
      
      // Serialize the PDF to bytes
      const pdfBytes = await pdfDoc.save();
      return pdfBytes;
      
    } catch (error) {
      console.error('Error generating PDF:', error);
      throw error;
    }
  },
  
  downloadPDF: async (pdfBytes: Uint8Array, filename: string) => {
    try {
      const blob = new Blob([pdfBytes], { type: 'application/pdf' });
      const url = URL.createObjectURL(blob);
      
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error downloading PDF:', error);
      throw error;
    }
  },
  
  generateSEPAMandat: async (data: {
    companyName: string;
    address: string;
    iban?: string;
    bic?: string;
    bankName?: string;
    mandateReference: string;
  }): Promise<Uint8Array> => {
    try {
      const pdfDoc = await PDFDocument.create();
      const helveticaFont = await pdfDoc.embedFont(StandardFonts.Helvetica);
      const helveticaBold = await pdfDoc.embedFont(StandardFonts.HelveticaBold);
      
      const page = pdfDoc.addPage([595, 842]); // A4
      const { width, height } = page.getSize();
      
      let yPosition = height - 50;
      const margin = 50;
      
      // Title
      page.drawText('SEPA-Lastschriftmandat', {
        x: margin,
        y: yPosition,
        size: 20,
        font: helveticaBold,
        color: rgb(0, 0, 0),
      });
      
      yPosition -= 40;
      
      // Mandate reference
      page.drawText(`Mandatsreferenz: ${data.mandateReference}`, {
        x: margin,
        y: yPosition,
        size: 12,
        font: helveticaBold,
        color: rgb(0, 0, 0),
      });
      
      yPosition -= 20;
      
      page.drawText('Gläubiger-Identifikationsnummer: DE83ZZZ00002415204', {
        x: margin,
        y: yPosition,
        size: 12,
        font: helveticaBold,
        color: rgb(0, 0, 0),
      });
      
      yPosition -= 40;
      
      // Authorization text
      const authText = `Ich ermächtige die EcomTask UG (haftungsbeschränkt), Zahlungen von meinem Konto mittels Lastschrift einzuziehen. Zugleich weise ich mein Kreditinstitut an, die von EcomTask UG auf mein Konto gezogenen Lastschriften einzulösen.

Hinweis: Ich kann innerhalb von acht Wochen, beginnend mit dem Belastungsdatum, die Erstattung des belasteten Betrages verlangen. Es gelten dabei die mit meinem Kreditinstitut vereinbarten Bedingungen.`;
      
      const authLines = authText.split('\n');
      for (const line of authLines) {
        page.drawText(line, {
          x: margin,
          y: yPosition,
          size: 11,
          font: helveticaFont,
          color: rgb(0, 0, 0),
          maxWidth: width - 2 * margin,
        });
        yPosition -= 20;
      }
      
      yPosition -= 20;
      
      // Company details
      page.drawText('Zahlungspflichtiger:', {
        x: margin,
        y: yPosition,
        size: 12,
        font: helveticaBold,
        color: rgb(0, 0, 0),
      });
      
      yPosition -= 20;
      
      page.drawText(data.companyName, {
        x: margin,
        y: yPosition,
        size: 11,
        font: helveticaFont,
        color: rgb(0, 0, 0),
      });
      
      yPosition -= 15;
      
      page.drawText(data.address, {
        x: margin,
        y: yPosition,
        size: 11,
        font: helveticaFont,
        color: rgb(0, 0, 0),
      });
      
      yPosition -= 40;
      
      // Bank details fields
      page.drawText('Bankverbindung:', {
        x: margin,
        y: yPosition,
        size: 12,
        font: helveticaBold,
        color: rgb(0, 0, 0),
      });
      
      yPosition -= 30;
      
      // IBAN field
      page.drawText('IBAN:', {
        x: margin,
        y: yPosition,
        size: 11,
        font: helveticaFont,
        color: rgb(0, 0, 0),
      });
      
      page.drawLine({
        start: { x: margin + 50, y: yPosition - 5 },
        end: { x: width - margin, y: yPosition - 5 },
        thickness: 1,
        color: rgb(0.7, 0.7, 0.7),
      });
      
      if (data.iban) {
        page.drawText(data.iban, {
          x: margin + 55,
          y: yPosition,
          size: 11,
          font: helveticaFont,
          color: rgb(0, 0, 0),
        });
      }
      
      yPosition -= 30;
      
      // BIC field
      page.drawText('BIC:', {
        x: margin,
        y: yPosition,
        size: 11,
        font: helveticaFont,
        color: rgb(0, 0, 0),
      });
      
      page.drawLine({
        start: { x: margin + 50, y: yPosition - 5 },
        end: { x: width - margin, y: yPosition - 5 },
        thickness: 1,
        color: rgb(0.7, 0.7, 0.7),
      });
      
      if (data.bic) {
        page.drawText(data.bic, {
          x: margin + 55,
          y: yPosition,
          size: 11,
          font: helveticaFont,
          color: rgb(0, 0, 0),
        });
      }
      
      yPosition -= 30;
      
      // Bank name field
      page.drawText('Bank:', {
        x: margin,
        y: yPosition,
        size: 11,
        font: helveticaFont,
        color: rgb(0, 0, 0),
      });
      
      page.drawLine({
        start: { x: margin + 50, y: yPosition - 5 },
        end: { x: width - margin, y: yPosition - 5 },
        thickness: 1,
        color: rgb(0.7, 0.7, 0.7),
      });
      
      if (data.bankName) {
        page.drawText(data.bankName, {
          x: margin + 55,
          y: yPosition,
          size: 11,
          font: helveticaFont,
          color: rgb(0, 0, 0),
        });
      }
      
      yPosition -= 60;
      
      // Signature area
      page.drawText('Ort, Datum:', {
        x: margin,
        y: yPosition,
        size: 11,
        font: helveticaFont,
        color: rgb(0, 0, 0),
      });
      
      page.drawLine({
        start: { x: margin + 80, y: yPosition - 5 },
        end: { x: margin + 250, y: yPosition - 5 },
        thickness: 1,
        color: rgb(0.7, 0.7, 0.7),
      });
      
      page.drawText('Unterschrift:', {
        x: margin + 300,
        y: yPosition,
        size: 11,
        font: helveticaFont,
        color: rgb(0, 0, 0),
      });
      
      page.drawLine({
        start: { x: margin + 380, y: yPosition - 5 },
        end: { x: width - margin, y: yPosition - 5 },
        thickness: 1,
        color: rgb(0.7, 0.7, 0.7),
      });
      
      // Footer
      const footerY = 50;
      page.drawText('Gläubiger:', {
        x: margin,
        y: footerY + 30,
        size: 10,
        font: helveticaBold,
        color: rgb(0.5, 0.5, 0.5),
      });
      
      page.drawText('EcomTask UG (haftungsbeschränkt)', {
        x: margin,
        y: footerY + 15,
        size: 10,
        font: helveticaFont,
        color: rgb(0.5, 0.5, 0.5),
      });
      
      page.drawText('Rauenthaler Straße 12, 65197 Wiesbaden', {
        x: margin,
        y: footerY,
        size: 10,
        font: helveticaFont,
        color: rgb(0.5, 0.5, 0.5),
      });
      
      const pdfBytes = await pdfDoc.save();
      return pdfBytes;
      
    } catch (error) {
      console.error('Error generating SEPA mandate PDF:', error);
      throw error;
    }
  }
};

export default pdfService; 