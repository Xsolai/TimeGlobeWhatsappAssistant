// Typen für das Onboarding-Formular
export interface OnboardingFormData {
  apiKey: string;
  companyName: string;
  street: string; // street_address in API
  city: string;
  zipCode: string; // postal_code in API
  country: string;
  contactPerson: string; // contact_person in API
  email: string;
  phone: string; // phone_number in API
  vatId: string; // tax_id in API, Umsatzsteuer-ID
  hasAcceptedTerms: boolean;
  signature: string | null;
  dataProcessingSignature: string | null; // Signatur für die Datenverarbeitungsvereinbarung
  directDebitSignature: string | null; // Signatur für das SEPA-Lastschriftmandat
  currentSignatureStep: number; // Aktueller Schritt im Unterschriftsprozess (0, 1, 2)
}

// Typen für die verschiedenen Schritte des Onboarding-Prozesses
export enum OnboardingStep {
  API_KEY = 'apiKey',
  COMPANY_INFO = 'companyInfo',
  CONTRACT = 'contract',
  CONFIRMATION = 'confirmation'
} 