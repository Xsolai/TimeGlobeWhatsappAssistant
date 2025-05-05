# TimeGlobe WhatsApp Chatbot Self-Onboarding Frontend

Dieses Projekt ist eine Frontend-Anwendung für das Self-Onboarding von Kunden für den TimeGlobe WhatsApp Chatbot.

## Features

- Mehrstufiger Onboarding-Prozess
- Erfassung von API-Schlüssel, Unternehmensinformationen
- Digitale Vertragsunterzeichnung
- Übersichtliche Bestätigungsansicht

## Technologien

- React 18
- TypeScript
- Material-UI
- React Signature Canvas für die Unterschriftenfunktion

## Installation

1. Repository klonen:
```
git clone <repository-url>
```

2. In das Projektverzeichnis wechseln:
```
cd selfonboarding-timeglobe
```

3. Abhängigkeiten installieren:
```
npm install
```

4. Anwendung starten:
```
npm start
```

Die Anwendung wird dann unter [http://localhost:3000](http://localhost:3000) geöffnet.

> **Wichtig:** Stellen Sie sicher, dass Sie die Befehle im Verzeichnis `selfonboarding-timeglobe` ausführen und nicht im übergeordneten Verzeichnis `Frontend_TimeGlobe`.

## Projektstruktur

```
src/
├── components/           # UI-Komponenten
│   ├── OnboardingForm.tsx  # Hauptkomponente für das Onboarding
│   └── steps/             # Komponenten für die einzelnen Schritte
│       ├── ApiKeyStep.tsx
│       ├── CompanyInfoStep.tsx
│       ├── ContractStep.tsx
│       └── ConfirmationStep.tsx
├── types/                # TypeScript-Definitionen
├── App.tsx               # Root-Komponente
└── index.tsx             # Einstiegspunkt
```

## Integration in bestehende Anwendungen

Um diese Komponente in eine bestehende Anwendung zu integrieren, kann die `OnboardingForm`-Komponente importiert und verwendet werden:

```tsx
import OnboardingForm from './components/OnboardingForm';

function YourApp() {
  return (
    <div>
      <h1>Ihre Anwendung</h1>
      <OnboardingForm />
    </div>
  );
}
```

## API-Endpunkte

Diese Frontend-Anwendung soll mit folgenden API-Endpunkten verbunden werden:

- `/api/validate-api-key` - Validierung des API-Schlüssels
- `/api/submit-onboarding` - Übermittlung der Onboarding-Daten

## Anpassungen

Um das Design an Ihre CI/CD anzupassen, können Sie das Theme in `App.tsx` bearbeiten:

```tsx
const theme = createTheme({
  palette: {
    primary: {
      main: '#IHRE_PRIMÄRFARBE',
    },
    secondary: {
      main: '#IHRE_SEKUNDÄRFARBE',
    },
  },
  // Weitere Anpassungen
});
```

## Entwickelt für TimeGlobe

Diese Anwendung wurde für TimeGlobe entwickelt, um den Onboarding-Prozess für WhatsApp Chatbot-Kunden zu vereinfachen.
