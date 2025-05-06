import React, { useRef, useState, useEffect } from 'react';
import { Box, Button, Typography, Checkbox, FormControlLabel, Paper, Alert, useTheme, Stepper, Step, StepLabel, StepButton } from '@mui/material';
import SignatureCanvas from 'react-signature-canvas';
import { OnboardingFormData } from '../../types';
import { PDFDocument, rgb } from 'pdf-lib';
import Description from '@mui/icons-material/Description';
import ArrowBack from '@mui/icons-material/ArrowBack';
import ArrowForward from '@mui/icons-material/ArrowForward';
import Edit from '@mui/icons-material/Edit';
import Delete from '@mui/icons-material/Delete';
import Check from '@mui/icons-material/Check';
import DescriptionOutlined from '@mui/icons-material/DescriptionOutlined';
import Article from '@mui/icons-material/Article';
import Payment from '@mui/icons-material/Payment';
import Download from '@mui/icons-material/Download';
import Upload from '@mui/icons-material/Upload';
import FileUpload from '@mui/icons-material/FileUpload';
import CloudUpload from '@mui/icons-material/CloudUpload';
import InfoOutlined from '@mui/icons-material/InfoOutlined';

interface ContractStepProps {
  formData: OnboardingFormData;
  onFormChange: (data: Partial<OnboardingFormData>) => void;
  onNext: () => void;
  onBack: () => void;
}

const ContractStep: React.FC<ContractStepProps> = ({ formData, onFormChange, onNext, onBack }) => {
  const [error, setError] = useState<string | null>(null);
  const [hasScrolledToBottom, setHasScrolledToBottom] = useState<boolean>(false);
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [uploadedFileName, setUploadedFileName] = useState<string>('');
  const [mandateReference, setMandateReference] = useState<string>('10001');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const signatureRef = useRef<SignatureCanvas>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const contractTextRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const theme = useTheme();
  
  // Verwende formData.currentSignatureStep für die Navigation zwischen den Unterschriftsschritten
  const currentStep = formData.currentSignatureStep || 0;

  // Definiere die Titel und Beschreibungen für die verschiedenen Vertragsschritte
  const contractSteps = [
    { 
      title: "Hauptvertrag", 
      description: "Bitte lesen Sie den Hauptvertrag sorgfältig durch und unterzeichnen Sie ihn.", 
      icon: <Description />,
      signatureField: "signature"
    },
    { 
      title: "Auftragsverarbeitung", 
      description: "Bitte bestätigen Sie die Vereinbarung zur Auftragsverarbeitung gemäß DSGVO.", 
      icon: <Article />,
      signatureField: "dataProcessingSignature"
    },
    { 
      title: "Lastschriftmandat", 
      description: "Bitte bestätigen Sie das SEPA-Lastschriftmandat für die monatlichen Zahlungen.", 
      icon: <Payment />,
      signatureField: "directDebitSignature"
    }
  ];

  // Lade die gespeicherte Mandatsreferenz beim Initialisieren
  useEffect(() => {
    const savedReference = localStorage.getItem('mandateReference');
    if (savedReference) {
      setMandateReference(savedReference);
    }
  }, []);

  // Aktualisiere Canvas-Größe bei Änderungen der Fenstergröße
  useEffect(() => {
    const resizeCanvas = () => {
      if (signatureRef.current && containerRef.current) {
        const canvas = signatureRef.current as any;
        const ratio = Math.max(window.devicePixelRatio || 1, 1);
        canvas.clear();
        canvas._canvas.width = containerRef.current.offsetWidth * ratio;
        canvas._canvas.height = 200 * ratio;
        canvas._canvas.getContext("2d").scale(ratio, ratio);
      }
    };

    window.addEventListener("resize", resizeCanvas);
    // Initial setzen
    setTimeout(resizeCanvas, 100);

    return () => window.removeEventListener("resize", resizeCanvas);
  }, [currentStep]);

  // Überwache den Scroll-Status des Vertragstextes
  const handleScroll = () => {
    const element = contractTextRef.current;
    if (element) {
      // Überprüfe, ob der Text bis zum Ende gescrollt wurde
      const isAtBottom = Math.abs(
        (element.scrollHeight - element.scrollTop) - element.clientHeight
      ) < 2;

      if (isAtBottom && !hasScrolledToBottom) {
        setHasScrolledToBottom(true);
      }
    }
  };

  const handleAcceptTermsChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (hasScrolledToBottom || formData.hasAcceptedTerms) {
      onFormChange({ hasAcceptedTerms: event.target.checked });
    }
  };

  const clearSignature = () => {
    if (signatureRef.current) {
      signatureRef.current.clear();
      
      // Setze die entsprechende Signatur basierend auf dem aktuellen Schritt zurück
      const signatureField = contractSteps[currentStep].signatureField;
      onFormChange({ [signatureField]: null });
    }
  };

  const saveSignature = () => {
    if (signatureRef.current) {
      if (signatureRef.current.isEmpty()) {
        setError('Bitte unterzeichnen Sie das Dokument');
        return;
      }
      
      const signatureData = signatureRef.current.toDataURL('image/png');
      
      // Speichere die Signatur im entsprechenden Feld basierend auf dem aktuellen Schritt
      const signatureField = contractSteps[currentStep].signatureField;
      onFormChange({ [signatureField]: signatureData });
      setError(null);
    }
  };

  const handleStepChange = (step: number) => {
    // Wechsle zu einem anderen Signaturschritt
    onFormChange({ currentSignatureStep: step });
    setHasScrolledToBottom(false);
    setError(null);
    
    // Lösche die Signatur, wenn der Canvas gewechselt wird
    if (signatureRef.current) {
      signatureRef.current.clear();
    }
  };

  const handleNextStep = () => {
    // Validiere den aktuellen Schritt
    if (currentStep === 0 && !formData.signature) {
      setError('Bitte unterzeichnen Sie den Hauptvertrag');
      return;
    } else if (currentStep === 1 && !formData.dataProcessingSignature) {
      setError('Bitte unterzeichnen Sie die Auftragsverarbeitung');
      return;
    }
    
    if (currentStep < 2) {
      // Gehe zum nächsten Unterschrittsschritt
      onFormChange({ currentSignatureStep: currentStep + 1 });
      setHasScrolledToBottom(false);
      setError(null);
    } else {
      // Alle drei Unterschriften sind abgeschlossen, gehe zum nächsten Hauptschritt
      onNext();
    }
  };

  const handlePrevStep = () => {
    if (currentStep > 0) {
      // Gehe zum vorherigen Unterschrittsschritt
      onFormChange({ currentSignatureStep: currentStep - 1 });
      setHasScrolledToBottom(false);
      setError(null);
    } else {
      // Gehe zum vorherigen Hauptschritt
      onBack();
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    // Überprüfe, ob alle erforderlichen Unterschriften vorhanden sind
    if (!formData.hasAcceptedTerms) {
      setError('Bitte akzeptieren Sie die Vertragsbedingungen');
      return;
    }
    
    if (currentStep === 0 && !formData.signature) {
      setError('Bitte unterzeichnen Sie den Hauptvertrag');
      return;
    } else if (currentStep === 1 && !formData.dataProcessingSignature) {
      setError('Bitte unterzeichnen Sie die Auftragsverarbeitung');
      return;
    } else if (currentStep === 2 && !formData.directDebitSignature) {
      setError('Bitte unterzeichnen Sie das Lastschriftmandat');
      return;
    }
    
    // Navigiere je nach aktuellem Schritt weiter
    handleNextStep();
  };

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (files && files.length > 0) {
      const file = files[0];
      
      // Prüfe, ob es eine PDF-Datei ist
      if (file.type !== 'application/pdf') {
        setError('Bitte laden Sie eine PDF-Datei hoch');
        return;
      }
      
      // Prüfe die Dateigröße (max. 5 MB)
      if (file.size > 5 * 1024 * 1024) {
        setError('Die Datei ist zu groß. Maximale Größe: 5 MB');
        return;
      }
      
      setUploadedFile(file);
      setUploadedFileName(file.name);
      
      // Speichere die Datei als Base64-String
      const reader = new FileReader();
      reader.onload = (e) => {
        const result = e.target?.result as string;
        // Speichere den Base64-String im formData
        onFormChange({ directDebitSignature: result });
        setError(null);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleDownloadSepaMandat = async () => {
    // Setze den Download-Button auf "Wird geladen..."
    setIsLoading(true);
    
    try {
      // Erhöhe die Mandatsreferenz um 1
      const currentRefNumber = parseInt(mandateReference, 10);
      const nextRefNumber = currentRefNumber + 1;
      const nextReference = nextRefNumber.toString().padStart(5, '0');
      
      // Speichere die neue Referenz im localStorage
      localStorage.setItem('mandateReference', nextReference);
      
      // Aktualisiere den State
      setMandateReference(nextReference);
      
      // Verwende eine direkte Download-Methode ohne PDF-Bearbeitung
      // Dies löst das Problem auf AWS Amplify, wo die PDF-Bearbeitung fehlschlägt
      const baseUrl = window.location.origin;
      const sepaDocumentUrl = `${baseUrl}/documents/LS-Mandat.pdf`;
      
      console.log('Versuche direkten Download von:', sepaDocumentUrl);
      
      // Hole den PDF-Inhalt als Blob
      const response = await fetch(sepaDocumentUrl, {
        method: 'GET',
        cache: 'no-store', // 'no-store' ist stärker als 'no-cache'
        headers: {
          'Accept': 'application/pdf',
        },
        mode: 'cors',
        credentials: 'same-origin',
      });
      
      if (!response.ok) {
        throw new Error(`PDF konnte nicht geladen werden: ${response.status} ${response.statusText}`);
      }
      
      // Überprüfe die Antwortgröße - sollte deutlich größer als 1KB sein
      const contentLength = response.headers.get('content-length');
      console.log(`Content-Length: ${contentLength} Bytes`);
      
      const blob = await response.blob();
      console.log(`Blob Größe: ${blob.size} Bytes`);
      
      // Verifiziere, dass wir eine gültige PDF-Datei erhalten haben
      if (blob.size < 5000) { // Ein minimales PDF sollte größer als 5KB sein
        console.error(`PDF scheint korrupt zu sein. Größe: ${blob.size} Bytes`);
        throw new Error('Die heruntergeladene Datei ist zu klein und möglicherweise beschädigt.');
      }
      
      // Erstelle eine URL für den Blob und trigger den Download
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `SEPA-Lastschriftmandat_${nextReference}.pdf`);
      
      // Verzögerung für bessere Browser-Kompatibilität
      setTimeout(() => {
        document.body.appendChild(link);
        link.click();
        
        // Bereinige nach einer kurzen Verzögerung
        setTimeout(() => {
          document.body.removeChild(link);
          URL.revokeObjectURL(url);
        }, 200);
      }, 100);
      
      console.log(`SEPA-Lastschriftmandat_${nextReference}.pdf Download initiiert`);
    } catch (error) {
      console.error('Fehler beim Herunterladen des PDFs:', error);
      
      // Alternativer Ansatz mit iframe für problematische Umgebungen
      try {
        console.log('Versuche alternative Download-Methode mit iframe...');
        const baseUrl = window.location.origin;
        const sepaDocumentUrl = `${baseUrl}/documents/LS-Mandat.pdf`;
        
        // Erstelle einen temporären iframe, der das PDF laden kann
        const iframe = document.createElement('iframe');
        iframe.style.display = 'none';
        document.body.appendChild(iframe);
        
        // Schreibe eine HTML-Seite mit Download-Link in den iframe
        iframe.contentWindow?.document.write(`
          <!DOCTYPE html>
          <html>
            <head>
              <title>PDF Download</title>
              <script>
                function downloadPdf() {
                  const link = document.createElement('a');
                  link.href = '${sepaDocumentUrl}';
                  link.download = 'SEPA-Lastschriftmandat_${mandateReference}.pdf';
                  document.body.appendChild(link);
                  link.click();
                  document.body.removeChild(link);
                }
                window.onload = downloadPdf;
              </script>
            </head>
            <body>
              Wenn der Download nicht automatisch startet, <a href="${sepaDocumentUrl}" download="SEPA-Lastschriftmandat_${mandateReference}.pdf">klicken Sie hier</a>.
            </body>
          </html>
        `);
        iframe.contentWindow?.document.close();
        
        // Entferne den iframe nach kurzer Zeit
        setTimeout(() => {
          document.body.removeChild(iframe);
        }, 5000);
        
        console.log('Alternative Download-Methode initiiert');
      } catch (iframeError) {
        console.error('Auch die alternative Methode ist fehlgeschlagen:', iframeError);
        
        // Letzte Fallback-Option: Öffne PDF in neuem Tab
        const baseUrl = window.location.origin;
        const sepaDocumentUrl = `${baseUrl}/documents/LS-Mandat.pdf`;
        window.open(sepaDocumentUrl, '_blank');
        
        alert('Der automatische Download konnte nicht durchgeführt werden. Das PDF wurde in einem neuen Tab geöffnet. Bitte speichern Sie es manuell ab.');
      }
    } finally {
      // Button-Status zurücksetzen
      setIsLoading(false);
    }
  };

  const triggerFileInput = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  // Bestimme, ob der aktuelle Schritt eine gültige Signatur hat
  const hasCurrentSignature = () => {
    switch (currentStep) {
      case 0: return !!formData.signature;
      case 1: return !!formData.dataProcessingSignature;
      case 2: return !!formData.directDebitSignature || !!uploadedFile;
      default: return false;
    }
  };

  return (
    <Box component="form" onSubmit={handleSubmit} sx={{ mt: 3, pb: 8 }}>
      {/* Dokumentenauswahl für die drei Vertragsschritte */}
      <Box sx={{ 
        mb: 4, 
        display: 'flex', 
        flexDirection: 'row',
        justifyContent: 'flex-start',
        alignItems: 'center',
        gap: 2
      }}>
        {contractSteps.map((step, index) => (
          <Box 
            key={index} 
            onClick={() => handleStepChange(index)}
            sx={{ 
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              cursor: 'pointer',
              p: 1.5,
              borderRadius: 2,
              backgroundColor: currentStep === index ? 'rgba(25, 103, 210, 0.1)' : 'transparent',
              border: currentStep === index ? '1px solid rgba(25, 103, 210, 0.3)' : '1px solid transparent',
              '&:hover': {
                backgroundColor: 'rgba(25, 103, 210, 0.05)'
              },
              transition: 'all 0.2s ease-in-out',
              width: 150
            }}
          >
            <Box sx={{ 
              width: 40, 
              height: 40, 
              borderRadius: '50%', 
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              backgroundColor: currentStep === index ? '#1967D2' : 'rgba(0, 0, 0, 0.1)',
              color: currentStep === index ? '#FFFFFF' : '#666666',
              mb: 1
            }}>
              {React.cloneElement(step.icon, { fontSize: 'small' })}
            </Box>
            <Typography 
              variant="body2"
              align="center"
              sx={{ 
                color: currentStep === index ? '#1967D2' : '#333333',
                fontWeight: currentStep === index ? 'medium' : 'normal',
                fontSize: '0.85rem',
                lineHeight: 1.2
              }}
            >
              {step.title}
            </Typography>
            {/* Statusindikator */}
            <Box 
              sx={{ 
                width: 8, 
                height: 8, 
                borderRadius: '50%', 
                mt: 1,
                backgroundColor: (
                  (index === 0 && !!formData.signature) || 
                  (index === 1 && !!formData.dataProcessingSignature) || 
                  (index === 2 && !!formData.directDebitSignature)
                ) ? '#4CAF50' : 'transparent'
              }}
            />
          </Box>
        ))}
      </Box>

      <Paper
        elevation={0}
        sx={{
          p: 3,
          mb: 4,
          borderRadius: 3,
          backgroundColor: '#FFFFFF',
          border: '1px solid #E0E0E0',
          boxShadow: '0 2px 8px rgba(0, 0, 0, 0.05)'
        }}
      >
        <Typography 
          variant="h6" 
          gutterBottom
          sx={{ 
            display: 'flex', 
            alignItems: 'center',
            color: '#333333',
            fontWeight: 'medium'
          }}
        >
          {contractSteps[currentStep].icon}
          <Box component="span" sx={{ ml: 1 }}>{contractSteps[currentStep].title}</Box>
        </Typography>
        
        <Typography variant="body2" sx={{ mb: 3, ml: 0.5, color: '#333333' }}>
          {contractSteps[currentStep].description}
        </Typography>
        
        {error && (
          <Alert 
            severity="error" 
            sx={{ 
              mb: 3, 
              borderRadius: 2,
              backgroundColor: 'rgba(211, 47, 47, 0.15)', 
              color: '#ff6b6b',
              '& .MuiAlert-icon': {
                color: '#ff6b6b'
              }
            }}
          >
            {error}
          </Alert>
        )}
        
        {/* Vertragstext basierend auf dem aktuellen Schritt */}
        {currentStep === 0 && (
          <Paper 
            ref={contractTextRef}
            variant="outlined" 
            sx={{ 
              p: 3, 
              mb: 3, 
              maxHeight: '300px', 
              overflow: 'auto',
              backgroundColor: 'rgba(0, 0, 0, 0.02)',
              borderRadius: 2,
              borderColor: 'rgba(0, 0, 0, 0.1)'
            }}
            onScroll={handleScroll}
          >
            <Typography variant="body2" sx={{ color: '#333333' }}>
              <strong>Vertrag über die Bereitstellung des<br />
              Add-ons "AI-Assistant" für den TimeGlobe-Kalender</strong>
              <br /><br />
              zwischen
              <br /><br />
              <span style={{ color: '#1967D2' }}>EcomTask UG<br />
              Rauenthaler Str. 12<br />
              65197 Wiesbaden<br />
              Deutschland</span>
              <br />
              (im Folgenden "EcomTask")
              <br /><br />
              und
              <br /><br />
              <span style={{ color: '#1967D2' }}>{formData.companyName || '[Unternehmensname]'}<br />
              {formData.street || '[Straße]'}<br />
              {formData.zipCode || '[PLZ]'} {formData.city || '[Stadt]'}<br />
              {formData.country || '[Land]'}</span>
              <br />
              (im Folgenden "Kunde")
              <br /><br />
              (EcomTask und Kunde einzeln jeweils auch "Partei" und gemeinsam "Parteien")
              <br /><br />
              {/* Gekürzte Version des Vertrags für die Übersichtlichkeit */}
              <strong>1. Vertragsgegenstand</strong><br />
              Gegenstand des Vertrags ist die entgeltliche und zeitlich auf die Dauer des Vertrags begrenzte Gewährung der Nutzung des Add-ons "AI-Assistent" für den TimeGlobe-Kalender (nachfolgend "Software") im Unternehmen des Kunden über das Internet. 
              <br /><br />
              <strong>2. Leistungen von EcomTask</strong><br />
              EcomTask gewährt dem Kunden (bzw. dessen Kunden) die Nutzung der jeweils aktuellen Version der Software mittels Zugriff durch WhatsApp.
              <br /><br />
              <strong>3. Nutzungsumfang und -rechte</strong><br />
              Der Kunde erhält an der jeweils aktuellen Version der Software einfache, d. h. nicht unterlizenzierbare und nicht übertragbare, zeitlich auf die Dauer des Vertrags beschränkte Rechte zur Nutzung.
              <br /><br />
              <strong>4. Vergütung</strong><br />
              Die monatliche Vergütung beträgt EUR ____.
              <br /><br />
              <strong>5. Vertragslaufzeit</strong><br />
              Der Vertrag wird auf unbestimmte Zeit geschlossen und kann mit einer Frist von X Monaten gekündigt werden.
              <br /><br />
              (Unterschriften der Parteien)
            </Typography>
          </Paper>
        )}
        
        {currentStep === 1 && (
          <Paper 
            ref={contractTextRef}
            variant="outlined" 
            sx={{ 
              p: 3, 
              mb: 3, 
              maxHeight: '300px', 
              overflow: 'auto',
              backgroundColor: 'rgba(0, 0, 0, 0.02)',
              borderRadius: 2,
              borderColor: 'rgba(0, 0, 0, 0.1)'
            }}
            onScroll={handleScroll}
          >
            <Typography variant="body2" sx={{ color: '#333333' }}>
              <strong>Auftragsverarbeitungsvertrag gemäß Art. 28 DSGVO</strong>
              <br /><br />
              zwischen
              <br /><br />
              <span style={{ color: '#1967D2' }}>{formData.companyName || '[Unternehmensname]'}<br />
              {formData.street || '[Straße]'}<br />
              {formData.zipCode || '[PLZ]'} {formData.city || '[Stadt]'}<br />
              {formData.country || '[Land]'}</span>
              <br />
              (im Folgenden "Verantwortlicher")
              <br /><br />
              und
              <br /><br />
              <span style={{ color: '#1967D2' }}>EcomTask UG<br />
              Rauenthaler Str. 12<br />
              65197 Wiesbaden<br />
              Deutschland</span>
              <br />
              (im Folgenden "Auftragsverarbeiter")
              <br /><br />
              
              <strong>1. Gegenstand und Dauer der Verarbeitung</strong><br />
              Der Auftragsverarbeiter verarbeitet personenbezogene Daten im Auftrag des Verantwortlichen im Zusammenhang mit der Bereitstellung des WhatsApp-Chatbots für die Terminplanung. Die Verarbeitung beginnt mit Aktivierung des Dienstes und endet mit Beendigung des Hauptvertrags.
              <br /><br />
              
              <strong>2. Art und Zweck der Verarbeitung</strong><br />
              Die Verarbeitung umfasst die Daten von Kunden, die über den WhatsApp-Chatbot Termine buchen. Zweck ist die Terminvergabe und -verwaltung.
              <br /><br />
              
              <strong>3. Kategorien betroffener Personen</strong><br />
              Betroffen sind Kunden des Verantwortlichen, die den WhatsApp-Chatbot zur Terminvereinbarung nutzen.
              <br /><br />
              
              <strong>4. Arten der personenbezogenen Daten</strong><br />
              Verarbeitet werden Kontaktdaten (Name, Telefonnummer), Termindetails und Kommunikationsverlauf.
              <br /><br />
              
              <strong>5. Pflichten des Auftragsverarbeiters</strong><br />
              Der Auftragsverarbeiter verarbeitet personenbezogene Daten ausschließlich im Rahmen der vertraglichen Vereinbarungen und nach Weisung des Verantwortlichen. Er gewährleistet angemessene technische und organisatorische Maßnahmen gemäß Art. 32 DSGVO.
              <br /><br />
              
              (Unterschriften der Parteien)
            </Typography>
          </Paper>
        )}

        {currentStep === 2 && (
          <Box>
            <Box sx={{ 
              display: 'flex', 
              justifyContent: 'space-between', 
              alignItems: 'center',
              mb: 3 
            }}>
              <Typography variant="subtitle1" sx={{ color: '#333333', fontWeight: 'medium' }}>
                SEPA-Lastschriftmandat
              </Typography>
              <Button
                variant="contained"
                size="medium"
                startIcon={<Download />}
                onClick={handleDownloadSepaMandat}
                disabled={isLoading}
                sx={{
                  borderRadius: 2,
                  backgroundColor: '#1967D2',
                  px: 3,
                  py: 1,
                  '&:hover': {
                    backgroundColor: '#1756B0',
                  }
                }}
              >
                {isLoading ? 'Wird bearbeitet...' : 'Mandat herunterladen'}
              </Button>
            </Box>
            
            <Box 
              sx={{ 
                backgroundColor: 'rgba(25, 103, 210, 0.05)', 
                p: 2, 
                borderRadius: 2, 
                mb: 3,
                display: 'flex',
                alignItems: 'flex-start'
              }}
            >
              <InfoOutlined sx={{ color: '#1967D2', mr: 1, mt: 0.5 }} />
              <Box>
                <Typography variant="subtitle2" sx={{ color: '#333333', mb: 0.5 }}>
                  Aktuelle Mandatsreferenznummer: {mandateReference}
                </Typography>
                <Typography variant="body2" sx={{ color: '#666666' }}>
                  Diese Nummer wird beim Download automatisch hochgezählt und im heruntergeladenen Dokument angezeigt.
                  Bitte verwenden Sie diese Nummer als Referenz.
                </Typography>
              </Box>
            </Box>
            
            <Typography variant="body2" sx={{ mb: 4, color: '#666666' }}>
              Bitte laden Sie das SEPA-Lastschriftmandat herunter, füllen Sie es aus, unterschreiben Sie es und laden Sie es anschließend wieder hoch.
            </Typography>
            
            <Box sx={{ mb: 4 }}>
              <Typography 
                variant="subtitle2" 
                sx={{ 
                  mb: 2, 
                  display: 'flex', 
                  alignItems: 'center',
                  color: '#333333' 
                }}
              >
                <FileUpload sx={{ mr: 1, fontSize: 20, color: '#1967D2' }} />
                Unterschriebenes SEPA-Mandat hochladen
              </Typography>
              
              <Box 
                sx={{ 
                  border: '2px dashed #1967D2',
                  borderRadius: 2,
                  backgroundColor: 'rgba(25, 103, 210, 0.05)',
                  p: 3,
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  justifyContent: 'center',
                  cursor: 'pointer',
                  mb: 2,
                  transition: 'all 0.2s ease-in-out',
                  '&:hover': {
                    backgroundColor: 'rgba(25, 103, 210, 0.08)',
                  }
                }}
                onClick={triggerFileInput}
              >
                <input
                  type="file"
                  accept=".pdf"
                  ref={fileInputRef}
                  onChange={handleFileUpload}
                  style={{ display: 'none' }}
                />
                
                {uploadedFile ? (
                  <>
                    <Check sx={{ fontSize: 40, color: '#4CAF50', mb: 1 }} />
                    <Typography variant="body2" sx={{ color: '#333333', fontWeight: 'medium' }}>
                      {uploadedFileName}
                    </Typography>
                    <Typography variant="caption" sx={{ color: '#666666', mt: 0.5 }}>
                      Datei erfolgreich hochgeladen. Klicken, um zu ändern.
                    </Typography>
                  </>
                ) : (
                  <>
                    <CloudUpload sx={{ fontSize: 40, color: '#1967D2', mb: 1 }} />
                    <Typography variant="body2" sx={{ color: '#333333' }}>
                      Datei hierher ziehen oder klicken
                    </Typography>
                    <Typography variant="caption" sx={{ color: '#666666', mt: 0.5 }}>
                      Unterstützte Dateiformate: PDF (max. 5 MB)
                    </Typography>
                  </>
                )}
              </Box>
            </Box>
            
            <Typography variant="body2" sx={{ color: '#666666', mb: 2 }}>
              <strong>Alternative:</strong> Sie können auch die digitale Unterschrift unten verwenden, um das Dokument direkt zu unterzeichnen.
            </Typography>
          </Box>
        )}
        
        {currentStep === 0 && (
          <FormControlLabel
            control={
              <Checkbox 
                checked={formData.hasAcceptedTerms} 
                onChange={handleAcceptTermsChange} 
                color="primary"
                disabled={!hasScrolledToBottom}
                icon={<Box sx={{ 
                  width: 20, 
                  height: 20, 
                  border: '2px solid rgba(0, 0, 0, 0.3)', 
                  borderRadius: 1,
                  ...(hasScrolledToBottom ? {} : { opacity: 0.5 })
                }} />}
                checkedIcon={<Box sx={{ 
                  width: 20, 
                  height: 20, 
                  borderRadius: 1,
                  backgroundColor: '#1967D2',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}>
                  <Check sx={{ color: '#fff', fontSize: 16 }} />
                </Box>}
              />
            }
            label={
              <Typography variant="body2" sx={{ color: '#666666' }}>
                {hasScrolledToBottom 
                  ? 'Ich akzeptiere die Vertragsbedingungen' 
                  : 'Bitte scrollen Sie den Vertrag vollständig durch, um die Bedingungen zu akzeptieren'}
              </Typography>
            }
            sx={{ mb: 3 }}
          />
        )}
        
        <Typography variant="subtitle1" gutterBottom sx={{ 
          display: 'flex', 
          alignItems: 'center',
          mt: 4,
          color: '#333333',
        }}>
          <Edit sx={{ mr: 1, fontSize: 20, opacity: 0.9, color: '#1967D2' }} />
          Ihre Unterschrift:
        </Typography>
        
        <Box 
          ref={containerRef}
          sx={{ 
            border: '1px solid rgba(0, 0, 0, 0.2)', 
            borderRadius: 2, 
            mb: 2,
            backgroundColor: '#FFFFFF',
            position: 'relative',
            overflow: 'hidden',
            height: '200px',
            '&::before': {
              content: '""',
              position: 'absolute',
              bottom: 0,
              left: 0,
              width: '100%',
              height: '5px',
              backgroundColor: '#1967D2',
              opacity: 0.5
            }
          }}
        >
          <SignatureCanvas 
            ref={signatureRef}
            canvasProps={{ 
              className: 'signature-canvas',
              style: { 
                width: '100%', 
                height: '100%', 
                cursor: 'crosshair'
              }
            }}
            backgroundColor="rgba(0, 0, 0, 0)"
            penColor="#000000"
            velocityFilterWeight={0}
            dotSize={0.5}
            minWidth={0.5}
            maxWidth={1.5}
            throttle={0}
          />
        </Box>
        
        <Box sx={{ display: 'flex', mb: 1 }}>
          <Button 
            onClick={clearSignature} 
            variant="outlined"
            startIcon={<Delete />}
            sx={{ 
              mr: 2,
              borderRadius: 2,
              borderColor: 'rgba(0, 0, 0, 0.2)',
              color: '#666666',
              '&:hover': {
                borderColor: '#f44336',
                backgroundColor: 'rgba(244, 67, 54, 0.08)'
              }
            }}
          >
            Löschen
          </Button>
          <Button 
            onClick={saveSignature} 
            variant="outlined"
            startIcon={<Check />}
            sx={{ 
              borderRadius: 2,
              borderColor: 'rgba(0, 0, 0, 0.2)',
              color: '#666666',
              '&:hover': {
                borderColor: '#1967D2',
                backgroundColor: 'rgba(25, 103, 210, 0.08)'
              }
            }}
          >
            Speichern
          </Button>
        </Box>
      </Paper>
      
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 3 }}>
        <Button 
          onClick={handlePrevStep}
          variant="outlined"
          startIcon={<ArrowBack />}
          sx={{ 
            borderRadius: 3,
            borderColor: '#1967D2',
            px: 3,
            py: 1.2,
            color: '#1967D2',
            '&:hover': {
              borderColor: '#1967D2',
              backgroundColor: 'rgba(25, 103, 210, 0.05)'
            }
          }}
        >
          {currentStep === 0 ? 'Zurück' : 'Vorherige'}
        </Button>
        <Button
          type="submit"
          variant="contained"
          color="primary"
          disabled={
            (currentStep === 0 && (!formData.hasAcceptedTerms || !formData.signature)) || 
            (currentStep === 1 && !formData.dataProcessingSignature) ||
            (currentStep === 2 && !formData.directDebitSignature)
          }
          endIcon={<ArrowForward />}
          sx={{ 
            px: 4, 
            py: 1.5,
            borderRadius: 3,
            boxShadow: '0 4px 15px rgba(0,0,0,0.2)',
            backgroundColor: '#1967D2',
            '&:hover': {
              boxShadow: '0 6px 20px rgba(0,0,0,0.3)',
              backgroundColor: '#1756B0',
            },
            '&.Mui-disabled': {
              backgroundColor: 'rgba(0, 0, 0, 0.12)',
              color: 'rgba(0, 0, 0, 0.3)'
            }
          }}
        >
          {currentStep < 2 ? 'Weiter' : 'Abschließen'}
        </Button>
      </Box>
    </Box>
  );
};

// Footer als eigenständige Komponente außerhalb des Hauptinhalts
const Footer = () => (
  <Box 
    sx={{ 
      position: 'fixed',
      bottom: 0,
      left: 0,
      width: '100%',
      display: 'flex', 
      justifyContent: 'center', 
      alignItems: 'center',
      py: 1,
      backgroundColor: '#FFFFFF',
      opacity: 1,
      zIndex: 10
    }}
  >
    <Typography 
      variant="body2" 
      sx={{ 
        color: '#000000',
        mr: 1,
        fontSize: '0.85rem'
      }}
    >
      powered by
    </Typography>
    <img 
      src="/images/EcomTask_logo.svg" 
      alt="EcomTask Logo" 
      style={{ height: '36px' }} 
    />
  </Box>
);

// Die gesamte App-Komponente mit Hauptinhalt und Footer
const ContractStepWithFooter: React.FC<ContractStepProps> = (props) => {
  return (
    <>
      <ContractStep {...props} />
      <Footer />
    </>
  );
};

export default ContractStepWithFooter; 