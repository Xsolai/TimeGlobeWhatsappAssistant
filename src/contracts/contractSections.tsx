import React from 'react';
import {
  Business,
  Assignment,
  Euro,
  Security,
  Gavel,
  DateRange,
  LocationOn,
  Person,
  Email,
  Phone
} from '@mui/icons-material';
import { Box, Typography, List, ListItem, ListItemText } from '@mui/material';

export interface ContractData {
  companyName: string;
  street: string;
  zipCode: string;
  city: string;
  country?: string;
  contactPerson: string;
  email?: string;
  phone?: string;
}

// Hauptvertrag Sektionen
export const getMainContractSections = (data: ContractData) => [
  {
    id: 'parties',
    title: '1. Vertragsgegenstand',
    icon: <Business />,
    content: `Gegenstand des Vertrags ist die entgeltliche und zeitlich auf die Dauer des Vertrags begrenzte Gewährung der Nutzung des Add-ons „AI-Assistant" für den TimeGlobe-Kalender (nachfolgend „Software") im Unternehmen des Kunden über das Internet. Gegenstand der Nutzung ist die KI-basierte Unterstützung des Kunden bei Terminvergabe und Terminplanung mit einem Chatbot für WhatsApp.`,
    required: true
  },
  {
    id: 'subject',
    title: '2. Leistungen von EcomTask; Software und Speicherplatz',
    icon: <Assignment />,
    content: `2.1 EcomTask gewährt dem Kunden (bzw. dessen Kunden) die Nutzung der jeweils aktuellen Version der Software mittels Zugriff durch WhatsApp.

2.2 EcomTask richtet den AI-Assistenten individuell für den Kunden ein. Dies umfasst die Anbindung an den bestehenden und bereits eingerichteten TimeGlobe-Kalender des Kunden. Eine weitergehende Anpassung auf die individuellen Bedürfnisse oder die IT-Umgebung des Kunden schuldet EcomTask im Übrigen nicht.

2.3 EcomTask gewährleistet die Funktionsfähigkeit und Verfügbarkeit der Software während der Dauer des Vertragsverhältnisses und wird diese in einem zum vertragsgemäßen Gebrauch geeigneten Zustand erhalten. Der Funktionsumfang der Software sowie die Einsatzbedingungen ergeben sich aus Anlage 1 zu diesem Vertrag. Voraussetzung ist auf jeden Fall, dass der Kunde über eine funktionsfähige Instanz des TimeGlobe-Kalenders verfügt und EcomTask Zugriff auf die von der TimeGlobe GmbH im Auftrag des Kunden bereitzustellende TimeGlobe API erhält.

2.4 EcomTask kann, ohne hierzu verpflichtet zu sein, die Software jederzeit aktualisieren oder weiterentwickeln und insbesondere aufgrund geänderter Rechtslage, technischer Entwicklungen oder zur Verbesserung der IT-Sicherheit anpassen. EcomTask wird dabei die berechtigten Interessen des Kunden angemessen berücksichtigen und den Kunden rechtzeitig über notwendige Anpassungen seiner Prozesse informieren. Im Falle einer wesentlichen Beeinträchtigung der berechtigten Interessen des Kunden steht diesem ein Sonderkündigungsrecht zu.

2.5 EcomTask wird die Software regelmäßig warten und den Kunden über etwaige hiermit verbundene Einschränkungen rechtzeitig informieren. Die Wartung wird regelmäßig außerhalb der üblichen Geschäftszeiten des Kunden durchgeführt, es sei denn, aufgrund zwingender Gründe muss eine Wartung zu einer anderen Zeit vorgenommen werden.

2.6 EcomTask wird dem Stand der Technik entsprechende Maßnahmen zum Schutz der Daten vornehmen. EcomTask treffen jedoch keine Verwahrungs- oder Obhutspflichten hinsichtlich der Daten des Kunden. Für eine ausreichende Sicherung der Daten ist der Kunde verantwortlich.

2.7 Der Kunde bleibt Inhaber der auf den Servern von EcomTask abgelegten Daten und kann diese jederzeit herausverlangen.`,
    required: true
  },
  {
    id: 'payment',
    title: '3. Nutzungsumfang und -rechte',
    icon: <Euro />,
    content: `3.1 Eine physische Überlassung der Software an den Kunden erfolgt nicht.

3.2 Der Kunde erhält an der jeweils aktuellen Version der Software einfache, d. h. nicht unterlizenzierbare und nicht übertragbare, zeitlich auf die Dauer des Vertrags beschränkte Rechte, die Software mittels Zugriff über WhatsApp nach Maßgabe der vertraglichen Regelungen für die Terminplanung mittels seines TimeGlobe-Kalenders zu nutzen.

3.3 Der Kunde darf die Software nur im Rahmen seiner eigenen geschäftlichen Tätigkeit durch eigenes Personal und Nutzer seines WhatsApp-Kanals (als Kundschaft seines Geschäfts) für die Terminvergabe und Terminplanung nutzen. Eine weitergehende Nutzung der Software ist nicht gestattet.`,
    required: true
  },
  {
    id: 'duration',
    title: '4. Support',
    icon: <DateRange />,
    content: `EcomTask richtet für Anfragen des Kunden zu Funktionen der Software einen Support-Service ein. Anfragen können über die auf der Website von EcomTask angegebene Support-Hotline zu den dort angegebenen Zeiten oder per E-Mail gestellt werden. Die Anfragen werden grundsätzlich in zeitlicher Reihenfolge ihres Eingangs bearbeitet.`,
    required: true
  },
  {
    id: 'service-levels',
    title: '5. Service Levels; Störungsbehebung',
    icon: <Security />,
    content: `5.1 EcomTask gewährt eine Gesamtverfügbarkeit der Leistungen von mindestens 98% im Monat am Übergabepunkt. Der Übergabepunkt ist der Routerausgang des Rechenzentrums von EcomTask.

5.2 Als Verfügbarkeit gilt die Möglichkeit des Kunden, sämtliche Hauptfunktionen der Software zu nutzen. Wartungszeiten sowie Zeiten der Störung unter Einhaltung der Behebungszeit gelten als Zeiten der Verfügbarkeit der Software. Zeiten unerheblicher Störungen bleiben bei der Berechnung der Verfügbarkeit ebenso außer Betracht wie Zeiten, in denen über die TimeGlobe API kein Zugriff für die Software auf den TimeGlobe-Kalender des Kunden möglich ist. Für den Nachweis der Verfügbarkeit sind die Messinstrumente von EcomTask im Rechenzentrum maßgeblich.

5.3 Der Kunde hat Störungen unverzüglich an den Support-Service (siehe Ziffer 4) zu melden. Eine Störungsmeldung und -behebung ist Montag bis Freitag (ausgenommen bundesweite Feiertage) zwischen 9 Uhr und 16 Uhr gewährleistet (Servicezeiten).

5.4 Schwerwiegende Störungen (die Nutzung der Software insgesamt oder eine Hauptfunktion der Software ist nicht möglich) wird EcomTask auch außerhalb der Servicezeiten spätestens binnen 12 Stunden ab Eingang der Meldung der Störung – sofern die Meldung innerhalb der Servicezeiten erfolgt – beheben (Behebungszeit). Sofern absehbar ist, dass eine Behebung der Störung nicht innerhalb dieser Zeitspanne möglich ist, wird er dem Kunde hierüber unverzüglich informieren und die voraussichtliche Überschreitung der Zeitspanne mitteilen.

5.5 Sonstige erhebliche Störungen (Haupt- oder Nebenfunktionen der Software sind gestört, können aber genutzt werden; oder andere nicht nur unerhebliche Störungen) werden spätestens binnen 48 Stunden innerhalb der Servicezeiten behoben (Behebungszeit).

5.6 Die Beseitigung von unerheblichen Störungen liegt im Ermessen von EcomTask.

5.7 EcomTask gewährleistet eine Lösungsfrist von 48 Stunden für 95 % der gemeldeten technischen Störungen. Bei Überschreitung dieser Frist hat der Kunde das Recht auf eine Minderung des monatlichen Retainers um 5 % pro angefangener 24-Stunden-Verzögerung.

5.8 Etwaige sonstige gesetzliche Ansprüche des Kunden gegen EcomTask bleiben unberührt.`,
    required: true
  },
  {
    id: 'customer-obligations',
    title: '6. Pflichten und Mitwirkung des Kunden',
    icon: <Gavel />,
    content: `6.1 Der Kunde hat die ihm ggf. übermittelten Zugangsdaten dem Stand der Technik entsprechend vor Zugriffen Dritter zu schützen und zu verwahren. Der Kunde wird dafür sorgen, dass eine Nutzung nur im vertraglich vereinbarten Umfang geschieht. Ein unberechtigter Zugriff (bzw. ein entsprechender Verdacht) ist EcomTask unverzüglich mitzuteilen.

6.2 Der Kunde hat während der Laufzeit dieses Vertrags eine funktionsfähige Instanz des TimeGlobe-Kalenders bereitzustellen und EcomTask über eine Schnittstelle (TimeGlobe-API) Zugriff auf den TimeGlobe-Kalender zu gewähren.

6.3 Der Kunde ergreift die nach Art. 4 KI-VO notwendigen Maßnahmen, um sicherzustellen, dass seine Nutzer über ein ausreichendes Maß an KI-Kompetenz verfügen. Dabei sind ihre technischen Kenntnisse, ihre Erfahrung, ihre Ausbildung und Schulung und der Kontext, in dem das System eingesetzt werden soll, zu berücksichtigen.`,
    required: true
  },
  {
    id: 'warranty',
    title: '7. Gewährleistung',
    icon: <Security />,
    content: `7.1 Hinsichtlich der Gewährung der Nutzung der Software sowie der Zurverfügungstellung von Speicherplatzes gelten die Gewährleistungsvorschriften des Mietrechts ( §§ 535 ff. BGB).

7.2 Der Kunde hat EcomTask jegliche Mängel unverzüglich anzuzeigen.

7.3 Die Gewährleistung für nur unerhebliche Minderungen der Tauglichkeit der Leistung wird ausgeschlossen. Die verschuldensunabhängige Haftung gem. § 536a Abs. 1 BGB für Mängel, die bereits bei Vertragsschluss vorlagen, ist ausgeschlossen.`,
    required: true
  },
  {
    id: 'obligations',
    title: '8. Haftung',
    icon: <Gavel />,
    content: `8.1 Die Parteien haften unbeschränkt bei Vorsatz, grober Fahrlässigkeit sowie bei schuldhafter Verletzung von Leben, Körper oder Gesundheit.

8.2 Unbeschadet der Fälle unbeschränkter Haftung gemäß Ziffer 8.1 haften die Parteien einander bei leicht fahrlässiger Pflichtverletzung nur bei Verletzung wesentlicher Vertragspflichten, also Pflichten, deren Erfüllung die ordnungsgemäße Durchführung des Vertrages überhaupt erst ermöglicht oder deren Verletzung die Erreichung des Vertragszwecks gefährdet und auf deren Einhaltung die andere Partei regelmäßig vertrauen darf, allerdings beschränkt auf den bei Vertragsschluss vorhersehbaren, vertragstypischen Schaden.

8.3 Die vorstehenden Haftungsbeschränkungen gelten nicht für die Haftung nach dem Produkthaftungsgesetz sowie im Rahmen schriftlich von einer Partei übernommener Garantien.

8.4 Diese Ziffer 8 gilt auch zu Gunsten von Mitarbeitern, Vertretern und Organen der Parteien.`
  },
  {
    id: 'legal-defects',
    title: '9. Rechtsmängel; Freistellung',
    icon: <Security />,
    content: `9.1 EcomTask gewährleistet, dass die Software keine Rechte Dritter verletzt. EcomTask wird dem Kunden von allen Ansprüchen Dritter wegen von ihm zu vertretender Schutzrechtsverletzungen im Zusammenhang mit der vertragsgemäßen Nutzung der Software auf erstes Anfordern hin freistellen sowie die Kosten einer angemessenen Rechtsverfolgung ersetzen. Der Kunde wird EcomTask unverzüglich über Ansprüche von Dritten, die diese aufgrund der vertragsgemäßen Nutzung der Software gegen ihn geltend machen, informieren und ihm sämtliche erforderlichen Vollmachten erteilen und Befugnisse einräumen, um die Ansprüche zu verteidigen.

9.2 Der Kunde sichert zu, dass die auf den Servern von EcomTask abgelegten Inhalte und Daten sowie dessen Nutzung und Bereitstellung durch EcomTask, nicht gegen geltendes Recht, behördliche Anordnungen, Rechte Dritter oder Vereinbarungen mit Dritten verstoßen. Der Kunde wird EcomTask von Ansprüchen, die Dritte aufgrund eines Verstoßes gegen diese Ziffer geltend machen, auf erstes Anfordern freistellen.`
  },
  {
    id: 'remuneration',
    title: '10. Vergütung und Zahlungsbedingungen; Preisanpassungen',
    icon: <Euro />,
    content: `10.1 Der Kunde hat monatlich eine monatliche Bereitstellungsgebühr in Höhe von 39 EUR sowie eine nutzungsabhängige Gebühr in Höhe von 0,99 EUR pro Buchungsvorgang, jeweils zuzüglich MwSt. in der jeweils anfallenden gesetzlichen Höhe, an EcomTask zu zahlen.
Buchungsvorgänge im vorstehenden Sinne sind jeweils: Terminbuchungen, Terminverschiebungen.

10.2 Die Rechnungsstellung erfolgt kalendermonatlich zum 10. des Folgemonats.

10.3 Die Zahlung ist im SEPA-Basis- oder SEPA-Firmen-Lastschriftverfahren möglich. Der Kunde ist verpflichtet, gegenüber EcomTask bei Vertragsschluss ein entsprechendes SEPA-Lastschriftmandat zu erteilen und für ausreichende Deckung des angegebenen Kontos Sorge zu tragen.

10.4 Der Einzug der Lastschrift erfolgt fünf Kalendertage nach Rechnungsstellung. Der Kunde hat dafür Sorge zu tragen, dass sein Konto zu diesem Zeitpunkt die erforderliche Deckung aufweist. Kosten, die aufgrund der Nichteinlösung oder der Rückbuchung einer Lastschrift entstehen, trägt der Kunde, soweit er die Nichteinlösung oder Rückbuchung zu vertreten hat.

10.5 EcomTask kann die Vergütung gemäß Ziffer 10.1 der allgemeinen Preisentwicklung, den Kosten für die Erbringung der vertraglichen Leistungen (z. B. nach Neueinführung oder Änderung von Steuern, anderen Abgaben oder sonstigen gesetzlichen Bestimmungen oder infolge eines Anstieges von Lohn-, Material-, Dienstleister- oder sonstigen Kosten) und/oder der aktuellen Preisliste für Neuverträge über den AI-Assistenten) anpassen. Die Anpassung wird frühestens 6 Wochen nach ihrer Ankündigung in Schriftform oder per E-Mail wirksam.`
  },
  {
    id: 'contract-duration',
    title: '11. Vertragslaufzeit und Beendigung',
    icon: <DateRange />,
    content: `11.1 Der Vertrag wird auf unbestimmte Zeit geschlossen und kann von beiden Parteien mit einer Frist von vier Wochen zum Monatsende gekündigt werden.

11.2 Das Recht zur fristlosen Kündigung aus wichtigem Grund bleibt unberührt.

11.3 Die Kündigung bedarf in jedem Fall der Schriftform.

11.4 EcomTask wird sämtliche auf seinen Servern verbleibenden Daten des Kunden 30 Tage nach Beendigung des Vertragsverhältnisses unwiederherstellbar löschen. Ein Zurückbehaltungsrecht oder Pfandrechte an den Daten zugunsten von EcomTask bestehen nicht.`
  },
  {
    id: 'data-protection',
    title: '12. Datenschutz; Geheimhaltung; Referenzkunde',
    icon: <Security />,
    content: `12.1 Die Parteien werden die für sie jeweils geltenden anwendbaren datenschutzrechtlichen Bestimmungen einhalten.

12.2 Soweit EcomTask im Auftrag des Kunden personenbezogene Daten verarbeitet, gilt vorrangig der in der Anlage 2 beigefügte Auftragsverarbeitungsvertrag gemäß Artikel 28 DSGVO.

12.3 EcomTask verpflichtet sich, über alle vertraulichen Informationen (einschließlich Geschäftsgeheimnissen), die EcomTask im Zusammenhang mit diesem Vertrag und dessen Durchführung erfährt, Stilschweigen zu bewahren und diese nicht gegenüber Dritten offenzulegen, weiterzugeben oder auf sonstige Art zu verwenden. Vertrauliche Informationen sind dabei solche, die als vertraulich gekennzeichnet sind oder deren Vertraulichkeit sich aus den Umständen ergibt, unabhängig davon, ob sie in schriftlicher, elektronischer, verkörperter oder mündlicher Form mitgeteilt worden sind. Die Geheimhaltungsverpflichtung gilt nicht, soweit EcomTask gesetzlich oder aufgrund bestands- bzw. rechtskräftiger Behörden- oder Gerichtsentscheidung zur Offenlegung der vertraulichen Information verpflichtet ist. EcomTask verpflichtet sich, mit allen Mitarbeitern und Subunternehmern eine den vorstehenden Absatz inhaltgleiche Regelung zu vereinbaren.

12.4 Ziffer 12.3 gilt nicht im Verhältnis zwischen EcomTask und der TimeGlobe GmbH, soweit es sich um Informationen handelt, die für die Einrichtung und den Betrieb der Software und ihre Anbindung an den TimeGlobe-Kalender notwendig sind und daher von EcomTask und der TimeGlobe GmbH ausgetauscht werden.

12.5 Der Kunde kann während der Dauer dieses Vertrags von EcomTask als Referenzkunde genannt werden. Die Angabe kann dabei auch online auf der Unternehmenswebseite von EcomTask und einschließlich der Nennung der Geschäfts-/Salonbezeichnung und ggf. des Firmenlogos des Kunden erfolgen.`
  },
  {
    id: 'final',
    title: '13. Schlussbestimmungen',
    icon: <Gavel />,
    content: `13.1 Sollten einzelne Regelungen dieses Vertrags unwirksam oder nicht durchführbar sein, bleibt die Wirksamkeit der übrigen Regelungen hiervon unberührt. Die Parteien werden solche Regelungen durch wirksame und durchführbare Regelungen ersetzen, die dem Sinn und wirtschaftlichen Zweck sowie dem Willen der Parteien bei Vertragsschluss möglichst gleichkommen. Entsprechendes gilt im Falle einer Vertragslücke.

13.2 Mündliche oder schriftliche Nebenabreden zu diesem Vertrag bestehen nicht. Änderungen dieses Vertrags und seiner Anlagen bedürfen der Schriftform.

13.3 Es gilt deutsches Recht unter Ausschluss der kollisionsrechtlichen Bestimmungen und des Übereinkommens der Vereinten Nationen über Verträge über den internationalen Warenverkauf vom 11.4.1980 (UN-Kaufrecht).

13.4 Ausschließlicher Gerichtsstand für alle Streitigkeiten aus oder im Zusammenhang mit diesem Vertrag ist Wiesbaden.`
  }
];

// Auftragsverarbeitungsvertrag Sektionen
export const getDataProcessingContractSections = (data: ContractData) => [
  {
    id: 'preamble',
    title: 'Präambel',
    icon: <Security />,
    content: `Zwischen dem Verantwortlichen und dem Auftragsverarbeiter besteht ein Auftragsverhältnis im Sinne des Art. 28 der Datenschutz-Grundverordnung (Verordnung (EU) 2016/679 des Europäischen Parlaments und des Rates vom 27. April 2016 zum Schutz natürlicher Personen bei der Verarbeitung personenbezogener Daten, zum freien Datenverkehr und zur Aufhebung der Richtlinie 95/46/EG, DSGVO").

Dieser Auftragsverarbeitungsvertrag einschließlich aller Anlagen (nachfolgend gemeinsam als "Vereinbarung" bezeichnet) konkretisiert die datenschutzrechtlichen Verpflichtungen der Parteien aus dem zugrundeliegenden Vertrag, der Leistungsvereinbarung und/oder Auftragsbeschreibung einschließlich aller Anlagen (nachfolgend gemeinsam als "Hauptvertrag" bezeichnet). Sofern Bezug auf die Regelungen des Bundesdatenschutzgesetzes (nachfolgend "BDSG") genommen wird, so ist damit das Gesetz zur Anpassung des Datenschutzrechts an die Verordnung (EU) 2016/679 und zur Umsetzung der Richtlinie (EU) 2016/680 in der zum Zeitpunkt ab dem 25. Mai 2018 geltenden Fassung gemeint.

Der Auftragsverarbeiter verpflichtet sich gegenüber dem Verantwortlichen zur Erfüllung des Hauptvertrages und dieser Vereinbarung nach Maßgabe der folgenden Bestimmungen:`,
    required: true
  },
  {
    id: 'subject-data',
    title: '§ 1 Anwendungsbereich und Begriffsbestimmungen',
    icon: <Assignment />,
    content: `(1) Die nachfolgenden Bestimmungen finden Anwendung auf alle Leistungen der Auftragsverarbeitung im Sinne des Art. 28 DSGVO, die der Auftragsverarbeiter auf Grundlage des Hauptvertrages gegenüber dem Verantwortlichen erbringt.

(2) Sofern in dieser Vereinbarung der Begriff „Datenverarbeitung" oder „Verarbeitung" von Daten benutzt wird, ist darunter allgemein die Verwendung von personenbezogenen Daten zu verstehen. Datenverarbeitung oder das Verarbeiten von Daten bezeichnet jeden mit oder ohne Hilfe automatisierter Verfahren ausgeführten Vorgang oder jede solche Vorgangsreihe im Zusammenhang mit personenbezogenen Daten wie das Erheben, das Erfassen, die Organisation, das Ordnen, die Speicherung, die Anpassung oder Veränderung, das Auslesen, das Abfragen, die Verwendung, die Offenlegung durch Übermittlung, Verbreitung oder eine andere Form der Bereitstellung, den Abgleich oder die Verknüpfung, die Einschränkung, das Löschen oder die Vernichtung.

(3) Auf die weiteren Begriffsbestimmungen in Art. 4 DSGVO wird verwiesen.`,
    required: true
  },
  {
    id: 'obligations',
    title: '§ 2 Gegenstand und Dauer der Datenverarbeitung',
    icon: <Gavel />,
    content: `(1) Der Auftragsverarbeiter verarbeitet personenbezogene Daten im Auftrag und nach Weisung des Verantwortlichen.

(2) Gegenstand des Auftrags ist die Bereitstellung eines Chat-Bots mit KI-Funktion auf WhatsApp im Rahmen des mit dem Auftragsverarbeiter vereinbarten Umfangs, gemäß dem Hauptvertrag.

(3) Die Dauer dieser Vereinbarung entspricht der Laufzeit des Hauptvertrages.`,
    required: true
  },
  {
    id: 'purpose-data',
    title: '§ 3 Art und Zweck der Datenverarbeitung',
    icon: <Assignment />,
    content: `Art und Zweck der Verarbeitung personenbezogener Daten durch den Auftragsverarbeiter ergeben sich aus dem Hauptvertrag. Dieser umfasst folgende Tätigkeit(en) und Zweck(e):

• Einsatz eines KI-gestützten Chatbots für den Kundenkontakt
• Automatisierung von Buchungsprozessen von Terminen einschließlich Koordinierung zwischen verschiedenen technischen Anwendung mittels Schnittstellen, insb. Microsoft Outlook, ERP-System, PDF-Dateienauswertung

im Übrigen wird auf den Hauptvertrag verwiesen`,
    required: true
  },
  {
    id: 'data-subjects',
    title: '§ 4 Kategorien betroffener Personen',
    icon: <Person />,
    content: `Im Rahmen dieser Vereinbarung werden personenbezogene Daten von folgenden Kategorien betroffener Personen verarbeitet:

• Kunden des Friseursalons des Verantwortlichen
• Mitarbeiter (Stammbelegschaft, Auszubildende, Leiharbeiter, freie Mitarbeiter)`,
    required: true
  },
  {
    id: 'data-types',
    title: '§ 5 Art der personenbezogenen Daten',
    icon: <Security />,
    content: `Von der Auftragsverarbeitung sind folgende Datenarten betroffen:

• Personenstammdaten (Name, Anrede, Titel/akademischer Grad, Geburtsdatum)
• Kontaktdaten (E-Mail-Adresse, Telefonnummer, Anschrift)
• Vertragsdaten (Vertragsdetails, Leistungen, Kundennummer)
• Kundenhistorie
• Vertragsabrechnungsdaten und Zahlungsinformationen (Rechnungsdetails, Bankverbindung, Kreditkarteninformationen)
• Beschäftigtendaten
• Elektronische Kommunikationsdaten (IP-Adresse, aufgerufene Internetseiten, Angaben zum verwendeten Endgerät, Betriebssystem und Browser)`,
    required: true
  },
  {
    id: 'controller-rights',
    title: '§ 6 Rechte und Pflichten des Verantwortlichen',
    icon: <Gavel />,
    content: `(1) Für die Beurteilung der Zulässigkeit der Datenverarbeitung sowie zur Wahrung der Rechte der Betroffenen ist allein der Verantwortliche zuständig und somit für die Verarbeitung Verantwortlicher im Sinne des Art. 4 Nr.7 DSGVO.

(2) Der Verantwortliche ist berechtigt, Weisungen über Art, Umfang und Verfahren der Datenverarbeitung zu erteilen. Mündliche Weisungen sind auf Verlangen des Auftragsverarbeiters unverzüglich vom Verantwortlichen schriftlich oder in Textform (z.B. per E-Mail) zu bestätigen.

(3) Soweit es der Verantwortliche für erforderlich hält, können weisungsberechtigte Personen benannt werden. Diese wird der Verantwortliche dem Auftragsverarbeiter schriftlich oder in Textform mitteilen. Für den Fall, dass sich diese weisungsberechtigten Personen bei dem Verantwortlichen ändern, wird dies dem Auftragsverarbeiter unter Benennung der jeweils neuen Person schriftlich oder in Textform mitgeteilt.

(4) Der Verantwortliche informiert den Auftragsverarbeiter unverzüglich, wenn Fehler oder Unregelmäßigkeiten im Zusammenhang mit der Verarbeitung personenbezogener Daten durch den Auftragsverarbeiter festgestellt werden.`,
    required: true
  },
  {
    id: 'tom',
    title: '§ 7 Pflichten des Auftragsverarbeiters',
    icon: <Security />,
    content: `(1) Datenverarbeitung

Der Auftragsverarbeiter wird personenbezogene Daten ausschließlich nach Maßgabe dieser Vereinbarung und/oder des zugrundeliegenden Hauptvertrages sowie nach den Weisungen des Verantwortlichen verarbeiten.

(2) Betroffenenrechte

a. Der Auftragsverarbeiter wird den Verantwortlichen bei der Erfüllung der Rechte der Betroffenen, insbesondere im Hinblick auf Berichtigung, Einschränkung der Verarbeitung und Löschung, Benachrichtigung und Auskunftserteilung, im Rahmen seiner Möglichkeiten unterstützen. Sollte der Auftragsverarbeiter die in § 5 dieser Vereinbarung genannten personenbezogenen Daten im Auftrag des Verantwortlichen verarbeiten und sind diese Daten Gegenstand eines Verlangens auf Datenportabilität gem. Art. 20 DSGVO, wird der Auftragsverarbeiter dem Verantwortlichen den betreffenden Datensatz innerhalb einer angemessen gesetzten Frist, im Übrigen innerhalb von sieben Arbeitstagen, in einem strukturierten, gängigen und maschinenlesbaren Format zur Verfügung stellen.

b. Der Auftragsverarbeiter hat auf Weisung des Verantwortlichen die in § 5 dieser Vereinbarung genannten personenbezogenen Daten, die im Auftrag verarbeitet werden, zu berichtigen, zu löschen oder die Verarbeitung einzuschränken. Das Gleiche gilt, wenn diese Vereinbarung eine Berichtigung, Löschung oder Einschränkung der Verarbeitung von Daten vorsieht.

c. Soweit sich eine betroffene Person unmittelbar an den Auftragsverarbeiter zwecks Berichtigung, Löschung oder Einschränkung der Verarbeitung der in § 5 dieser Vereinbarung genannten personenbezogenen Daten wendet, wird der Auftragsverarbeiter dieses Ersuchen unverzüglich nach Erhalt an den Verantwortlichen weiterleiten.

(3) Kontrollpflichten

a. Der Auftragsverarbeiter stellt durch geeignete Kontrollen sicher, dass die im Auftrag verarbeiteten personenbezogenen Daten ausschließlich nach Maßgabe dieser Vereinbarung und/oder des Hauptvertrages und/oder den entsprechenden Weisungen verarbeitet werden.

b. Der Auftragsverarbeiter wird sein Unternehmen und seine Betriebsabläufe so gestalten, dass die Daten, die er im Auftrag des Verantwortlichen verarbeitet, im jeweils erforderlichen Maß gesichert und vor der unbefugten Kenntnisnahme Dritter geschützt sind.

c. Der Auftragsverarbeiter bestätigt, dass er gem. Art. 37 DSGVO und, sofern anwendbar, gemäß § 38 BDSG einen Datenschutzbeauftragten bestellt hat und die Einhaltung der Vorschriften zum Datenschutz und zur Datensicherheit unter Einbeziehung des Datenschutzbeauftragten überwacht. Datenschutzbeauftragter des Auftragsverarbeiters ist derzeit:

ISiCO Datenschutz GmbH
+49 30 21300285-0
info@isico-datenschutz.de

(4) Informationspflichten

a. Der Auftragsverarbeiter wird den Verantwortlichen unverzüglich darauf aufmerksam machen, wenn eine von dem Verantwortlichen erteilte Weisung seiner Meinung nach gegen gesetzliche Vorschriften verstößt. Der Auftragsverarbeiter ist berechtigt, die Durchführung der entsprechenden Weisung solange auszusetzen, bis sie durch den Verantwortlichen bestätigt oder geändert wird.

b. Der Auftragsverarbeiter wird den Verantwortlichen bei der Einhaltung der in den Artikeln 32 bis 36 DSGVO genannten Pflichten unter Berücksichtigung der Art der Verarbeitung und der ihm zur Verfügung stehenden Informationen unterstützen.

(5) Ort der Datenverarbeitung

Die Verarbeitung der Daten findet grundsätzlich im Gebiet der Bundesrepublik Deutschland, in einem Mitgliedsstaat der Europäischen Union oder in einem anderen Vertragsstaat des Abkommens über den Europäischen Wirtschaftsraum statt. Jede Verlagerung in ein Drittland darf nur erfolgen, wenn die besonderen Voraussetzungen der Art. 44 ff. DSGVO erfüllt sind.

(6) Löschung der personenbezogenen Daten nach Auftragsbeendigung

Nach Beendigung des Hauptvertrages wird der Auftragsverarbeiter alle im Auftrag verarbeiteten personenbezogenen Daten nach Wahl des Verantwortlichen entweder löschen oder zurückgeben, sofern der Löschung dieser Daten keine gesetzlichen Aufbewahrungspflichten des Auftragsverarbeiters entgegenstehen. Die datenschutzgerechte Löschung ist zu dokumentieren und gegenüber dem Verantwortlichen auf Anforderung zu bestätigen.`
  },
  {
    id: 'subprocessors',
    title: '§ 8 Kontrollrechte des Verantwortlichen',
    icon: <Business />,
    content: `(1) Der Verantwortliche ist berechtigt, nach rechtzeitiger vorheriger Anmeldung zu den üblichen Geschäftszeiten ohne Störung des Geschäftsbetriebes des Auftragsverarbeiters oder Gefährdung der Sicherheitsmaßnahmen für andere Verantwortliche und auf eigene Kosten, die Einhaltung der Vorschriften über den Datenschutz und der vertraglichen Vereinbarungen im erforderlichen Umfang selbst oder durch Dritte zu kontrollieren. Die Kontrollen können auch durch Zugriff auf vorhandene branchenübliche Zertifizierungen des Auftragsverarbeiters aktuelle Testate oder Berichte einer unabhängigen Instanz (wie z.B. Wirtschaftsprüfer, externer Datenschutzbeauftragter, Revisor oder externer Datenschutzauditor) oder Selbstauskünfte durchgeführt werden. Der Auftragsverarbeiter wird die notwendige Unterstützung zur Durchführung der Kontrollen anbieten.

(2) Der Auftragsverarbeiter wird den Verantwortlichen über die Durchführung von Kontrollmaßnahmen der Aufsichtsbehörde informieren, soweit die Maßnahmen oder Datenverarbeitungen betreffen können, die der Auftragsverarbeiter für den Verantwortlichen erbringt.`
  },
  {
    id: 'unterauftragsverarbeiter',
    title: '§ 9 Unterauftragsverhältnisse',
    icon: <Business />,
    content: `(1) Der Verantwortliche ermächtigt den Auftragsverarbeiter weitere Auftragsverarbeiter gemäß den nachfolgenden Absätzen in § 9 dieser Vereinbarung in Anspruch zu nehmen. Diese Ermächtigung stellt eine allgemeine schriftliche Genehmigung i. S. d. Art. 28 Abs. 2 DSGVO dar.

(2) Der Auftragsverarbeiter arbeitet derzeit bei der Erfüllung des Auftrags mit den in der Anlage 2 benannten Unterauftragnehmern zusammen, mit deren Beauftragung sich der Verantwortliche einverstanden erklärt.

(3) Der Auftragsverarbeiter ist berechtigt, weitere Auftragsverarbeiter zu beauftragen oder bereits beauftragte zu ersetzen. Der Auftragsverarbeiter wird den Verantwortlichen vorab über jede beabsichtigte Änderung in Bezug auf die Hinzuziehung oder die Ersetzung eines weiteren Auftragsverarbeiters informieren. Der Verantwortliche kann gegen eine beabsichtigte Änderung Einspruch erheben.

(4) Der Einspruch gegen die beabsichtigte Änderung ist innerhalb von 2 Wochen nach Zugang der Information über die Änderung gegenüber dem Auftragsverarbeiter zu erheben. Im Fall des Einspruchs kann der Auftragsverarbeiter nach eigener Wahl die Leistung ohne die beabsichtigte Änderung erbringen oder einen alternativen weiteren Auftragsverarbeiter vorschlagen und mit dem Verantwortlichen abstimmen. Sofern die Erbringung der Leistung ohne die beabsichtigte Änderung dem Auftragsverarbeiter nicht zumutbar ist – etwa aufgrund von damit verbundenen unverhältnismäßigen Aufwendungen für den Auftragsverarbeiter – oder die Abstimmung eines weiteren Auftragsverarbeiters fehlschlägt, können der Verantwortliche und der Auftragsverarbeiter diese Vereinbarung sowie den Hauptvertrag außerordentlich zum Zeitpunkt des Inkrafttretens der beabsichtigten Änderung kündigen.

(5) Bei Einschaltung eines weiteren Auftragsverarbeiters muss stets ein Schutzniveau, welches mit demjenigen dieser Vereinbarung vergleichbar ist, gewährleistet werden. Der Auftragsverarbeiter ist gegenüber dem Verantwortlichen für sämtliche Handlungen und Unterlassungen der von ihm eingesetzten weiteren Auftragsverarbeiter verantwortlich.`
  },
  {
    id: 'rights',
    title: '§ 10 Vertraulichkeit',
    icon: <Person />,
    content: `(1) Der Auftragsverarbeiter ist bei der Verarbeitung von Daten für den Verantwortlichen zur Wahrung der Vertraulichkeit verpflichtet.

(2) Der Auftragsverarbeiter verpflichtet sich bei der Erfüllung des Auftrags nur Mitarbeiter oder sonstige Erfüllungsgehilfen einzusetzen, die auf die Vertraulichkeit im Umgang mit überlassenen personenbezogenen Daten verpflichtet und in geeigneter Weise mit den Anforderungen des Datenschutzes vertraut gemacht worden sind. Die Vornahme der Verpflichtungen wird der Auftragsverarbeiter dem Verantwortlichen auf Nachfrage nachweisen.

(3) Sofern der Verantwortliche anderweitigen Geheimnisschutzregeln unterliegt, wird er dies dem Auftragsverarbeiter mitteilen. Der Auftragsverarbeiter wird seine Mitarbeiter entsprechend den Anforderungen des Verantwortlichen auf diese Geheimnisschutzregeln verpflichten.`
  },
  {
    id: 'tom-measures',
    title: '§ 11 Technische und organisatorische Maßnahmen',
    icon: <Security />,
    content: `(1) Die in Anlage 1 beschriebenen technischen und organisatorischen Maßnahmen werden als angemessen vereinbart. Der Auftragsverarbeiter kann diese Maßnahmen aktualisieren und ändern, vorausgesetzt dass das Schutzniveau durch solche Aktualisierungen und/oder Änderungen nicht wesentlich herabgesetzt wird.

(2) Der Auftragsverarbeiter beachtet die Grundsätze ordnungsgemäßer Datenverarbeitung gemäß Art. 32 i.V.m Art. 5 Abs. 1 DSGVO. Er gewährleistet die vertraglich vereinbarten und gesetzlich vorgeschriebenen Datensicherheitsmaßnahmen. Er wird alle erforderlichen Maßnahmen zur Sicherung der Daten bzw. der Sicherheit der Verarbeitung, insbesondere auch unter Berücksichtigung des Standes der Technik, sowie zur Minderung möglicher nachteiliger Folgen für Betroffene ergreifen. Die zu treffenden Maßnahmen umfassen insbesondere Maßnahmen zum Schutz der Vertraulichkeit, Integrität, Verfügbarkeit und Belastbarkeit der Systeme und Maßnahmen, die die Kontinuität der Verarbeitung nach Zwischenfällen gewährleisten. Um stets ein angemessenes Sicherheitsniveau der Verarbeitung gewährleisten zu können, wird der Auftragsverarbeiter die implementierten Maßnahmen regelmäßig evaluieren und ggf. Anpassungen vornehmen.`
  },
  {
    id: 'liability-indemnification',
    title: '§ 12 Haftung/ Freistellung',
    icon: <Gavel />,
    content: `(1) Der Auftragsverarbeiter haftet gegenüber dem Verantwortlichen gemäß den gesetzlichen Regelungen für sämtliche Schäden durch schuldhafte Verstöße gegen diese Vereinbarung sowie gegen die ihn treffenden gesetzlichen Datenschutzbestimmungen, die der Auftragsverarbeiter, seine Mitarbeiter bzw. die von ihm mit der Vertragsdurchführung Beauftragten bei der Erbringung der vertraglichen Leistung verursachen. Eine Ersatzpflicht des Auftragsverarbeiters besteht nicht, sofern der Auftragsverarbeiter nachweist, dass er die ihm überlassenen Daten des Verantwortlichen ausschließlich nach den Weisungen des Verantwortlichen verarbeitet und seinen speziell den Auftragsverarbeitern auferlegten Pflichten aus der DSGVO nachgekommen ist.

(2) Der Verantwortliche stellt den Auftragsverarbeiter von allen Ansprüchen Dritter frei, die aufgrund einer schuldhaften Verletzung der Verpflichtungen aus dieser Vereinbarung oder geltenden datenschutzrechtlichen Vorschriften durch den Verantwortlichen gegen den Auftragsverarbeiter geltend gemacht werden.`
  },
  {
    id: 'audit',
    title: '§ 13 Sonstiges',
    icon: <Assignment />,
    content: `(1) Im Falle von Widersprüchen zwischen den Bestimmungen in dieser Vereinbarung und den Regelungen des Hauptvertrages gehen die Bestimmungen dieser Vereinbarung vor.

(2) Änderungen und Ergänzungen dieser Vereinbarung setzen die beidseitige Zustimmung der Vertragsparteien voraus unter konkreter Bezugnahme auf die zu ändernde Regelung dieser Vereinbarung. Mündliche Nebenabreden bestehen nicht und sich auch für künftige Änderungen dieser Vereinbarung ausgeschlossen.

(3) Diese Vereinbarung unterliegt deutschem Recht.

(4) Sofern der Zugriff auf die Daten, die der Verantwortliche dem Auftragsverarbeiter zur Datenverarbeitung übermittelt hat, durch Maßnahmen Dritter (z.B. Maßnahmen eines Insolvenzverwalters, Beschlagnahme durch Finanzbehörden, etc.) gefährdet wird, hat der Auftragsverarbeiter den Verantwortlichen unverzüglich hierüber zu benachrichtigen.`
  }
];

// SEPA-Mandat Sektionen
export const getSepaMandateSections = (data: ContractData, mandateReference: string) => [
  {
    id: 'mandate-info',
    title: 'Mandatsinformationen',
    icon: <Euro />,
    content: (
      <Box>
        <Box sx={{ bgcolor: 'info.light', p: 2, borderRadius: 1, mb: 2 }}>
          <Typography variant="body2" sx={{ fontWeight: 'bold', mb: 1 }}>
            Mandatsreferenz: {mandateReference}
          </Typography>
          <Typography variant="body2">
            Gläubiger-Identifikationsnummer: DE83ZZZ00002415204
          </Typography>
        </Box>
        
        <Typography variant="body2" paragraph>
          Ich ermächtige die EcomTask UG (haftungsbeschränkt), Zahlungen von meinem Konto mittels 
          Lastschrift einzuziehen. Zugleich weise ich mein Kreditinstitut an, die von EcomTask UG 
          auf mein Konto gezogenen Lastschriften einzulösen.
        </Typography>
        
        <Typography variant="body2" sx={{ fontStyle: 'italic' }}>
          Hinweis: Ich kann innerhalb von acht Wochen, beginnend mit dem Belastungsdatum, die 
          Erstattung des belasteten Betrages verlangen. Es gelten dabei die mit meinem Kreditinstitut 
          vereinbarten Bedingungen.
        </Typography>
      </Box>
    ),
    required: true
  },
  {
    id: 'creditor',
    title: 'Zahlungsempfänger',
    icon: <Business />,
    content: (
      <Box>
        <Typography variant="body2" sx={{ fontWeight: 'bold', mb: 1 }}>
          Gläubiger:
        </Typography>
        <Typography variant="body2">
          EcomTask UG (haftungsbeschränkt)<br />
          Rauenthaler Straße 12<br />
          65197 Wiesbaden<br />
          Deutschland
        </Typography>
        <Box sx={{ mt: 2 }}>
          <Typography variant="body2">
            <strong>E-Mail:</strong> info@ecomtask.de<br />
            <strong>Telefon:</strong> +49 (0) 611 123456<br />
            <strong>Handelsregister:</strong> HRB 12345, Amtsgericht Wiesbaden
          </Typography>
        </Box>
      </Box>
    )
  },
  {
    id: 'debtor',
    title: 'Zahlungspflichtiger',
    icon: <Person />,
    content: (
      <Box>
        <Typography variant="body2" sx={{ fontWeight: 'bold', mb: 1 }}>
          Kontoinhaber:
        </Typography>
        <Typography variant="body2">
          {data.companyName}<br />
          {data.street}<br />
          {data.zipCode} {data.city}<br />
          {data.country || 'Deutschland'}
        </Typography>
        {data.contactPerson && (
          <Typography variant="body2" sx={{ mt: 2 }}>
            <strong>Ansprechpartner:</strong> {data.contactPerson}
          </Typography>
        )}
      </Box>
    ),
    required: true
  },
  {
    id: 'bank-details',
    title: 'Bankverbindung',
    icon: <Euro />,
    content: (
      <Box>
        <Typography variant="body2" paragraph>
          Bitte tragen Sie Ihre Bankverbindung in das heruntergeladene PDF-Formular ein:
        </Typography>
        <Box sx={{ bgcolor: 'action.hover', p: 2, borderRadius: 1 }}>
          <Typography variant="body2">
            <strong>IBAN:</strong> _________________________________<br /><br />
            <strong>BIC:</strong> _________________________________<br /><br />
            <strong>Bank:</strong> _________________________________
          </Typography>
        </Box>
      </Box>
    ),
    required: true
  },
  {
    id: 'authorization',
    title: 'Ermächtigung',
    icon: <Gavel />,
    content: `Mit meiner Unterschrift bestätige ich:

• Die Richtigkeit der angegebenen Daten
• Die Ermächtigung zum Einzug von Lastschriften
• Die Kenntnisnahme meiner Widerrufsrechte

Die Mandatserteilung kann jederzeit widerrufen werden. Ein Widerruf gilt nur für zukünftige 
Zahlungen und berührt nicht die Wirksamkeit bereits durchgeführter Lastschriften.

Änderungen der Bankverbindung sind EcomTask UG unverzüglich mitzuteilen.`,
    required: true
  }
]; 