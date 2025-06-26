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

export interface DateRangeData {
  available_dates: string[];
}

export interface DashboardSummary {
  today_appointments?: number;
  today_cancelled?: number;
  todays_services?: number;
  costs_today?: number;
  costs_last_30_days?: number;
  monthly_appointments: number;
  monthly_cancelled: number;
  monthly_services_booked: number;
  monthly_growth_rate: number;
}

export interface AppointmentActivity {
  booking_id: number;
  service_name: string;
  appointment_date: string;
  appointment_time: string;
  customer_name: string;
  customer_phone: string;
  status: 'booked' | 'cancelled';
  service_names?: string[];
}

export interface TimeSeriesData {
  date: string;
  count: number;
  services: number;
  cancelled: number;
}

export interface DashboardData {
  summary: DashboardSummary;
  recent_appointments: AppointmentActivity[];
  appointment_time_series: TimeSeriesData[];
} 