/**
 * Main contract text for TimeGlobe AI Assistant
 * Last updated: 2025-05-16
 */

/**
 * Get the main contract text with placeholders that will be replaced with actual values
 */
export const getMainContractText = (
  companyName: string = '[Name]',
  street: string = '[Anschrift]',
  zipCode: string = '[PLZ]',
  city: string = '[Ort]',
  contactPerson: string = '[Ansprechpartner]'
): string => {
  return `Vertrag über die Bereitstellung des
Add-ons „AI-Assistant" für den TimeGlobe-Kalender


zwischen
EcomTask UG
vertreten durch Nick Wirth,
Rauenthaler Straße 12, 
65197, Wiesbaden, 
(im Folgenden „EcomTask")

 
und


${companyName}
vertreten durch ${contactPerson},
${street},
${zipCode}, ${city},
(im Folgenden „Kunde")

(EcomTask und Kunde einzeln jeweils auch „Partei" und gemeinsam „Parteien")

Vertragsgegenstand
Gegenstand des Vertrags ist die entgeltliche und zeitlich auf die Dauer des Vertrags begrenzte Gewährung der Nutzung des Add-ons „AI-Assistent" für den TimeGlobe-Kalender (nachfolgend „Software") im Unternehmen des Kunden über das Internet. Gegenstand der Nutzung ist die KI-basierte Unterstützung des Kunden bei Terminvergabe und Terminplanung mit einem Chatbot für WhatsApp.
Leistungen von EcomTask; Software und Speicherplatz
EcomTask gewährt dem Kunden (bzw. dessen Kunden) die Nutzung der jeweils aktuellen Version der Software mittels Zugriff durch WhatsApp.
EcomTask richtet den AI-Assistenten individuell für den Kunden ein. Dies umfasst die Anbindung an den bestehenden und bereits eingerichteten TimeGlobe-Kalender des Kunden. Eine weitergehende Anpassung auf die individuellen Bedürfnisse oder die IT-Umgebung des Kunden schuldet EcomTask im Übrigen nicht.
EcomTask gewährleistet die Funktionsfähigkeit und Verfügbarkeit der Software während der Dauer des Vertragsverhältnisses und wird diese in einem zum vertragsgemäßen Gebrauch geeigneten Zustand erhalten. Der Funktionsumfang der Software sowie die Einsatzbedingungen ergeben sich aus Anlage 1 zu diesem Vertrag. Voraussetzung ist auf jeden Fall, dass der Kunde über eine funktionsfähige Instanz des TimeGlobe-Kalenders verfügt und EcomTask Zugriff auf die von der TimeGlobe GmbH im Auftrag des Kunden bereitzustellende TimeGlobe API erhält.
EcomTask kann, ohne hierzu verpflichtet zu sein, die Software jederzeit aktualisieren oder weiterentwickeln und insbesondere aufgrund geänderter Rechtslage, technischer Entwicklungen oder zur Verbesserung der IT-Sicherheit anpassen. EcomTask wird dabei die berechtigten Interessen des Kunden angemessen berücksichtigen und den Kunden rechtzeitig über notwendige Anpassungen seiner Prozesse informieren. Im Falle einer wesentlichen Beeinträchtigung der berechtigten Interessen des Kunden steht diesem ein Sonderkündigungsrecht zu.
EcomTask wird die Software regelmäßig warten und den Kunden über etwaige hiermit verbundene Einschränkungen rechtzeitig informieren. Die Wartung wird regelmäßig außerhalb der üblichen Geschäftszeiten des Kunden durchgeführt, es sei denn, aufgrund zwingender Gründe muss eine Wartung zu einer anderen Zeit vorgenommen werden.
EcomTask wird dem Stand der Technik entsprechende Maßnahmen zum Schutz der Daten vornehmen. EcomTask treffen jedoch keine Verwahrungs- oder Obhutspflichten hinsichtlich der Daten des Kunden. Für eine ausreichende Sicherung der Daten ist der Kunde verantwortlich.
Der Kunde bleibt Inhaber der auf den Servern von EcomTask abgelegten Daten und kann diese jederzeit herausverlangen.

Nutzungsumfang und -rechte
Eine physische Überlassung der Software an den Kunden erfolgt nicht.
Der Kunde erhält an der jeweils aktuellen Version der Software einfache, d. h. nicht unterlizenzierbare und nicht übertragbare, zeitlich auf die Dauer des Vertrags beschränkte Rechte, die Software mittels Zugriff über WhatsApp nach Maßgabe der vertraglichen Regelungen für die Terminplanung mittels seines TimeGlobe-Kalenders zu nutzen.
Der Kunde darf die Software nur im Rahmen seiner eigenen geschäftlichen Tätigkeit durch eigenes Personal und Nutzer seines WhatsApp-Kanals (als Kundschaft seines Geschäfts) für die Terminvergabe und Terminplanung nutzen. Eine weitergehende Nutzung der Software ist nicht gestattet.
 
Support 
EcomTask richtet für Anfragen des Kunden zu Funktionen der Software einen Support-Service ein. Anfragen können über die auf der Website von EcomTask angegebene Support-Hotline zu den dort angegebenen Zeiten oder per E-Mail gestellt werden. Die Anfragen werden grundsätzlich in zeitlicher Reihenfolge ihres Eingangs bearbeitet.

Service Levels; Störungsbehebung
EcomTask gewährt eine Gesamtverfügbarkeit der Leistungen von mindestens 98% im Monat am Übergabepunkt. Der Übergabepunkt ist der Routerausgang des Rechenzentrums von EcomTask.
Als Verfügbarkeit gilt die Möglichkeit des Kunden, sämtliche Hauptfunktionen der Software zu nutzen. Wartungszeiten sowie Zeiten der Störung unter Einhaltung der Behebungszeit gelten als Zeiten der Verfügbarkeit der Software. Zeiten unerheblicher Störungen bleiben bei der Berechnung der Verfügbarkeit ebenso außer Betracht wie Zeiten, in denen über die TimeGlobe API kein Zugriff für die Software auf den TimeGlobe-Kalender des Kunden möglich ist. Für den Nachweis der Verfügbarkeit sind die Messinstrumente von EcomTask im Rechenzentrum maßgeblich.
Der Kunde hat Störungen unverzüglich an den Support-Service (siehe Ziffer 4) zu melden. Eine Störungsmeldung und -behebung ist Montag bis Freitag (ausgenommen bundesweite Feiertage) zwischen 9 Uhr und 16 Uhr gewährleistet (Servicezeiten).
Schwerwiegende Störungen (die Nutzung der Software insgesamt oder eine Hauptfunktion der Software ist nicht möglich) wird EcomTask auch außerhalb der Servicezeiten spätestens binnen 12 Stunden ab Eingang der Meldung der Störung – sofern die Meldung innerhalb der Servicezeiten erfolgt – beheben (Behebungszeit). Sofern absehbar ist, dass eine Behebung der Störung nicht innerhalb dieser Zeitspanne möglich ist, wird er dem Kunde hierüber unverzüglich informieren und die voraussichtliche Überschreitung der Zeitspanne mitteilen.
Sonstige erhebliche Störungen (Haupt- oder Nebenfunktionen der Software sind gestört, können aber genutzt werden; oder andere nicht nur unerhebliche Störungen) werden spätestens binnen 48 Stunden innerhalb der Servicezeiten behoben (Behebungszeit).
Die Beseitigung von unerheblichen Störungen liegt im Ermessen von EcomTask.
EcomTask gewährleistet eine Lösungsfrist von 48 Stunden für 95 % der gemeldeten technischen Störungen. Bei Überschreitung dieser Frist hat der Kunde das Recht auf eine Minderung des monatlichen Retainers um 5 % pro angefangener 24-Stunden-Verzögerung.
Etwaige sonstige gesetzliche Ansprüche des Kunden gegen EcomTask bleiben unberührt.

Pflichten und Mitwirkung des Kunden 
Der Kunde hat die ihm ggf. übermittelten Zugangsdaten dem Stand der Technik entsprechend vor Zugriffen Dritter zu schützen und zu verwahren. Der Kunde wird dafür sorgen, dass eine Nutzung nur im vertraglich vereinbarten Umfang geschieht. Ein unberechtigter Zugriff (bzw. ein entsprechender Verdacht) ist EcomTask unverzüglich mitzuteilen.
Der Kunde hat während der Laufzeit dieses Vertrags eine funktionsfähige Instanz des TimeGlobe-Kalenders bereitzustellen und EcomTask über eine Schnittstelle (TimeGlobe-API) Zugriff auf den TimeGlobe-Kalender zu gewähren.
Der Kunde ergreift die nach Art. 4 KI-VO notwendigen Maßnahmen, um sicherzustellen, dass seine Nutzer über ein ausreichendes Maß an KI-Kompetenz verfügen. Dabei sind ihre technischen Kenntnisse, ihre Erfahrung, ihre Ausbildung und Schulung und der Kontext, in dem das System eingesetzt werden soll, zu berücksichtigen.

Gewährleistung 
Hinsichtlich der Gewährung der Nutzung der Software sowie der Zurverfügungstellung von Speicherplatzes gelten die Gewährleistungsvorschriften des Mietrechts ( §§ 535 ff. BGB).
Der Kunde hat EcomTask jegliche Mängel unverzüglich anzuzeigen.
Die Gewährleistung für nur unerhebliche Minderungen der Tauglichkeit der Leistung wird ausgeschlossen. Die verschuldensunabhängige Haftung gem. § 536a Abs. 1 BGB für Mängel, die bereits bei Vertragsschluss vorlagen, ist ausgeschlossen.
 
Haftung
Die Parteien haften unbeschränkt bei Vorsatz, grober Fahrlässigkeit sowie bei schuldhafter Verletzung von Leben, Körper oder Gesundheit.
Unbeschadet der Fälle unbeschränkter Haftung gemäß Ziffer 8.1 haften die Parteien einander bei leicht fahrlässiger Pflichtverletzung nur bei Verletzung wesentlicher Vertragspflichten, also Pflichten, deren Erfüllung die ordnungsgemäße Durchführung des Vertrages überhaupt erst ermöglicht oder deren Verletzung die Erreichung des Vertragszwecks gefährdet und auf deren Einhaltung die andere Partei regelmäßig vertrauen darf, allerdings beschränkt auf den bei Vertragsschluss vorhersehbaren, vertragstypischen Schaden.
Die vorstehenden Haftungsbeschränkungen gelten nicht für die Haftung nach dem Produkthaftungsgesetz sowie im Rahmen schriftlich von einer Partei übernommener Garantien.
Diese Ziffer 8 gilt auch zu Gunsten von Mitarbeitern, Vertretern und Organen der Parteien. 
 
Rechtsmängel; Freistellung
EcomTask gewährleistet, dass die Software keine Rechte Dritter verletzt. EcomTask wird dem Kunden von allen Ansprüchen Dritter wegen von ihm zu vertretender Schutzrechtsverletzungen im Zusammenhang mit der vertragsgemäßen Nutzung der Software auf erstes Anfordern hin freistellen sowie die Kosten einer angemessenen Rechtsverfolgung ersetzen. Der Kunde wird EcomTask unverzüglich über Ansprüche von Dritten, die diese aufgrund der vertragsgemäßen Nutzung der Software gegen ihn geltend machen, informieren und ihm sämtliche erforderlichen Vollmachten erteilen und Befugnisse einräumen, um die Ansprüche zu verteidigen.
Der Kunde sichert zu, dass die auf den Servern von EcomTask abgelegten Inhalte und Daten sowie dessen Nutzung und Bereitstellung durch EcomTask, nicht gegen geltendes Recht, behördliche Anordnungen, Rechte Dritter oder Vereinbarungen mit Dritten verstoßen. Der Kunde wird EcomTask von Ansprüchen, die Dritte aufgrund eines Verstoßes gegen diese Ziffer geltend machen, auf erstes Anfordern freistellen.
 
Vergütung und Zahlungsbedingungen; Preisanpassungen
Der Kunde hat monatlich eine monatliche Bereitstellungsgebühr in Höhe von 39 EUR sowie eine nutzungsabhängige Gebühr in Höhe von 0,99 EUR pro Buchungsvorgang, jeweils zuzüglich MwSt. in der jeweils anfallenden gesetzlichen Höhe, an EcomTask zu zahlen.
Buchungsvorgänge im vorstehenden Sinne sind jeweils: Terminbuchungen, Terminverschiebungen.
Die Rechnungsstellung erfolgt kalendermonatlich zum 10. des Folgemonats.
Die Zahlung ist im SEPA-Basis- oder SEPA-Firmen-Lastschriftverfahren möglich. Der Kunde ist verpflichtet, gegenüber EcomTask bei Vertragsschluss ein entsprechendes SEPA-Lastschriftmandat zu erteilen und für ausreichende Deckung des angegebenen Kontos Sorge zu tragen.
Der Einzug der Lastschrift erfolgt fünf Kalendertage nach Rechnungsstellung. Der Kunde hat dafür Sorge zu tragen, dass sein Konto zu diesem Zeitpunkt die erforderliche Deckung aufweist. Kosten, die aufgrund der Nichteinlösung oder der Rückbuchung einer Lastschrift entstehen, trägt der Kunde, soweit er die Nichteinlösung oder Rückbuchung zu vertreten hat.
EcomTask kann die Vergütung gemäß Ziffer 10.1 der allgemeinen Preisentwicklung, den Kosten für die Erbringung der vertraglichen Leistungen (z. B. nach Neueinführung oder Änderung von Steuern, anderen Abgaben oder sonstigen gesetzlichen Bestimmungen oder infolge eines Anstieges von Lohn-, Material-, Dienstleister- oder sonstigen Kosten) und/oder der aktuellen Preisliste für Neuverträge über den AI-Assistenten) anpassen. Die Anpassung wird frühestens 6 Wochen nach ihrer Ankündigung in Schriftform oder per E-Mail wirksam.
 
Vertragslaufzeit und Beendigung 
Der Vertrag wird auf unbestimmte Zeit geschlossen und kann von beiden Parteien mit einer Frist von vier Wochen zum Monatsende gekündigt werden.
Das Recht zur fristlosen Kündigung aus wichtigem Grund bleibt unberührt.
Die Kündigung bedarf in jedem Fall der Schriftform.
EcomTask wird sämtliche auf seinen Servern verbleibenden Daten des Kunden 30 Tage nach Beendigung des Vertragsverhältnisses unwiederherstellbar löschen. Ein Zurückbehaltungsrecht oder Pfandrechte an den Daten zugunsten von EcomTask bestehen nicht.   
 
Datenschutz; Geheimhaltung; Referenzkunde
Die Parteien werden die für sie jeweils geltenden anwendbaren datenschutzrechtlichen Bestimmungen einhalten.
Soweit EcomTask im Auftrag des Kunden personenbezogene Daten verarbeitet, gilt vorrangig der in der Anlage 2 beigefügte Auftragsverarbeitungsvertrag gemäß Artikel 28 DSGVO.
EcomTask verpflichtet sich, über alle vertraulichen Informationen (einschließlich Geschäftsgeheimnissen), die EcomTask im Zusammenhang mit diesem Vertrag und dessen Durchführung erfährt, Stilschweigen zu bewahren und diese nicht gegenüber Dritten offenzulegen, weiterzugeben oder auf sonstige Art zu verwenden. Vertrauliche Informationen sind dabei solche, die als vertraulich gekennzeichnet sind oder deren Vertraulichkeit sich aus den Umständen ergibt, unabhängig davon, ob sie in schriftlicher, elektronischer, verkörperter oder mündlicher Form mitgeteilt worden sind. Die Geheimhaltungsverpflichtung gilt nicht, soweit EcomTask gesetzlich oder aufgrund bestands- bzw. rechtskräftiger Behörden- oder Gerichtsentscheidung zur Offenlegung der vertraulichen Information verpflichtet ist. EcomTask verpflichtet sich, mit allen Mitarbeitern und Subunternehmern eine den vorstehenden Absatz inhaltgleiche Regelung zu vereinbaren.
Ziffer 12.3 gilt nicht im Verhältnis zwischen EcomTask und der TimeGlobe GmbH, soweit es sich um Informationen handelt, die für die Einrichtung und den Betrieb der Software und ihre Anbindung an den TimeGlobe-Kalender notwendig sind und daher von EcomTask und der TimeGlobe GmbH ausgetauscht werden.
Der Kunde kann während der Dauer dieses Vertrags von EcomTask als Referenzkunde genannt werden. Die Angabe kann dabei auch online auf der Unternehmenswebseite von EcomTask und einschließlich der Nennung der Geschäfts-/Salonbezeichnung und ggf. des Firmenlogos des Kunden erfolgen.

Schlussbestimmungen
Sollten einzelne Regelungen dieses Vertrags unwirksam oder nicht durchführbar sein, bleibt die Wirksamkeit der übrigen Regelungen hiervon unberührt. Die Parteien werden solche Regelungen durch wirksame und durchführbare Regelungen ersetzen, die dem Sinn und wirtschaftlichen Zweck sowie dem Willen der Parteien bei Vertragsschluss möglichst gleichkommen. Entsprechendes gilt im Falle einer Vertragslücke.
Mündliche oder schriftliche Nebenabreden zu diesem Vertrag bestehen nicht. Änderungen dieses Vertrags und seiner Anlagen bedürfen der Schriftform.
Es gilt deutsches Recht unter Ausschluss der kollisionsrechtlichen Bestimmungen und des Übereinkommens der Vereinten Nationen über Verträge über den internationalen Warenverkauf vom 11.4.1980 (UN-Kaufrecht).
Ausschließlicher Gerichtsstand für alle Streitigkeiten aus oder im Zusammenhang mit diesem Vertrag ist Wiesbaden.
`;
};

/**
 * Get a shorter preview version of the main contract for display in UI
 */
export const getMainContractPreviewText = (
  companyName: string = '[Name]',
  street: string = '[Anschrift]',
  zipCode: string = '[PLZ]',
  city: string = '[Ort]',
  contactPerson: string = '[Ansprechpartner]'
): string => {
  return `Vertrag über die Bereitstellung des
Add-ons „AI-Assistant" für den TimeGlobe-Kalender


zwischen
EcomTask UG
vertreten durch Nick Wirth,
Rauenthaler Straße 12, 
65197, Wiesbaden, 
(im Folgenden „EcomTask")

 
und


${companyName}
vertreten durch ${contactPerson},
${street},
${zipCode}, ${city},
(im Folgenden „Kunde")

(EcomTask und Kunde einzeln jeweils auch „Partei" und gemeinsam „Parteien")

Vertragsgegenstand
Gegenstand des Vertrags ist die entgeltliche und zeitlich auf die Dauer des Vertrags begrenzte Gewährung der Nutzung des Add-ons „AI-Assistent" für den TimeGlobe-Kalender (nachfolgend „Software") im Unternehmen des Kunden über das Internet. Gegenstand der Nutzung ist die KI-basierte Unterstützung des Kunden bei Terminvergabe und Terminplanung mit einem Chatbot für WhatsApp.
Leistungen von EcomTask; Software und Speicherplatz
EcomTask gewährt dem Kunden (bzw. dessen Kunden) die Nutzung der jeweils aktuellen Version der Software mittels Zugriff durch WhatsApp.
EcomTask richtet den AI-Assistenten individuell für den Kunden ein. Dies umfasst die Anbindung an den bestehenden und bereits eingerichteten TimeGlobe-Kalender des Kunden. Eine weitergehende Anpassung auf die individuellen Bedürfnisse oder die IT-Umgebung des Kunden schuldet EcomTask im Übrigen nicht.
EcomTask gewährleistet die Funktionsfähigkeit und Verfügbarkeit der Software während der Dauer des Vertragsverhältnisses und wird diese in einem zum vertragsgemäßen Gebrauch geeigneten Zustand erhalten. Der Funktionsumfang der Software sowie die Einsatzbedingungen ergeben sich aus Anlage 1 zu diesem Vertrag. Voraussetzung ist auf jeden Fall, dass der Kunde über eine funktionsfähige Instanz des TimeGlobe-Kalenders verfügt und EcomTask Zugriff auf die von der TimeGlobe GmbH im Auftrag des Kunden bereitzustellende TimeGlobe API erhält.
EcomTask kann, ohne hierzu verpflichtet zu sein, die Software jederzeit aktualisieren oder weiterentwickeln und insbesondere aufgrund geänderter Rechtslage, technischer Entwicklungen oder zur Verbesserung der IT-Sicherheit anpassen. EcomTask wird dabei die berechtigten Interessen des Kunden angemessen berücksichtigen und den Kunden rechtzeitig über notwendige Anpassungen seiner Prozesse informieren. Im Falle einer wesentlichen Beeinträchtigung der berechtigten Interessen des Kunden steht diesem ein Sonderkündigungsrecht zu.
EcomTask wird die Software regelmäßig warten und den Kunden über etwaige hiermit verbundene Einschränkungen rechtzeitig informieren. Die Wartung wird regelmäßig außerhalb der üblichen Geschäftszeiten des Kunden durchgeführt, es sei denn, aufgrund zwingender Gründe muss eine Wartung zu einer anderen Zeit vorgenommen werden.
EcomTask wird dem Stand der Technik entsprechende Maßnahmen zum Schutz der Daten vornehmen. EcomTask treffen jedoch keine Verwahrungs- oder Obhutspflichten hinsichtlich der Daten des Kunden. Für eine ausreichende Sicherung der Daten ist der Kunde verantwortlich.
Der Kunde bleibt Inhaber der auf den Servern von EcomTask abgelegten Daten und kann diese jederzeit herausverlangen.

Nutzungsumfang und -rechte
Eine physische Überlassung der Software an den Kunden erfolgt nicht.
Der Kunde erhält an der jeweils aktuellen Version der Software einfache, d. h. nicht unterlizenzierbare und nicht übertragbare, zeitlich auf die Dauer des Vertrags beschränkte Rechte, die Software mittels Zugriff über WhatsApp nach Maßgabe der vertraglichen Regelungen für die Terminplanung mittels seines TimeGlobe-Kalenders zu nutzen.
Der Kunde darf die Software nur im Rahmen seiner eigenen geschäftlichen Tätigkeit durch eigenes Personal und Nutzer seines WhatsApp-Kanals (als Kundschaft seines Geschäfts) für die Terminvergabe und Terminplanung nutzen. Eine weitergehende Nutzung der Software ist nicht gestattet.
 
Support 
EcomTask richtet für Anfragen des Kunden zu Funktionen der Software einen Support-Service ein. Anfragen können über die auf der Website von EcomTask angegebene Support-Hotline zu den dort angegebenen Zeiten oder per E-Mail gestellt werden. Die Anfragen werden grundsätzlich in zeitlicher Reihenfolge ihres Eingangs bearbeitet.

Service Levels; Störungsbehebung
EcomTask gewährt eine Gesamtverfügbarkeit der Leistungen von mindestens 98% im Monat am Übergabepunkt. Der Übergabepunkt ist der Routerausgang des Rechenzentrums von EcomTask.
Als Verfügbarkeit gilt die Möglichkeit des Kunden, sämtliche Hauptfunktionen der Software zu nutzen. Wartungszeiten sowie Zeiten der Störung unter Einhaltung der Behebungszeit gelten als Zeiten der Verfügbarkeit der Software. Zeiten unerheblicher Störungen bleiben bei der Berechnung der Verfügbarkeit ebenso außer Betracht wie Zeiten, in denen über die TimeGlobe API kein Zugriff für die Software auf den TimeGlobe-Kalender des Kunden möglich ist. Für den Nachweis der Verfügbarkeit sind die Messinstrumente von EcomTask im Rechenzentrum maßgeblich.
Der Kunde hat Störungen unverzüglich an den Support-Service (siehe Ziffer 4) zu melden. Eine Störungsmeldung und -behebung ist Montag bis Freitag (ausgenommen bundesweite Feiertage) zwischen 9 Uhr und 16 Uhr gewährleistet (Servicezeiten).
Schwerwiegende Störungen (die Nutzung der Software insgesamt oder eine Hauptfunktion der Software ist nicht möglich) wird EcomTask auch außerhalb der Servicezeiten spätestens binnen 12 Stunden ab Eingang der Meldung der Störung – sofern die Meldung innerhalb der Servicezeiten erfolgt – beheben (Behebungszeit). Sofern absehbar ist, dass eine Behebung der Störung nicht innerhalb dieser Zeitspanne möglich ist, wird er dem Kunde hierüber unverzüglich informieren und die voraussichtliche Überschreitung der Zeitspanne mitteilen.
Sonstige erhebliche Störungen (Haupt- oder Nebenfunktionen der Software sind gestört, können aber genutzt werden; oder andere nicht nur unerhebliche Störungen) werden spätestens binnen 48 Stunden innerhalb der Servicezeiten behoben (Behebungszeit).
Die Beseitigung von unerheblichen Störungen liegt im Ermessen von EcomTask.
EcomTask gewährleistet eine Lösungsfrist von 48 Stunden für 95 % der gemeldeten technischen Störungen. Bei Überschreitung dieser Frist hat der Kunde das Recht auf eine Minderung des monatlichen Retainers um 5 % pro angefangener 24-Stunden-Verzögerung.
Etwaige sonstige gesetzliche Ansprüche des Kunden gegen EcomTask bleiben unberührt.

Pflichten und Mitwirkung des Kunden 
Der Kunde hat die ihm ggf. übermittelten Zugangsdaten dem Stand der Technik entsprechend vor Zugriffen Dritter zu schützen und zu verwahren. Der Kunde wird dafür sorgen, dass eine Nutzung nur im vertraglich vereinbarten Umfang geschieht. Ein unberechtigter Zugriff (bzw. ein entsprechender Verdacht) ist EcomTask unverzüglich mitzuteilen.
Der Kunde hat während der Laufzeit dieses Vertrags eine funktionsfähige Instanz des TimeGlobe-Kalenders bereitzustellen und EcomTask über eine Schnittstelle (TimeGlobe-API) Zugriff auf den TimeGlobe-Kalender zu gewähren.
Der Kunde ergreift die nach Art. 4 KI-VO notwendigen Maßnahmen, um sicherzustellen, dass seine Nutzer über ein ausreichendes Maß an KI-Kompetenz verfügen. Dabei sind ihre technischen Kenntnisse, ihre Erfahrung, ihre Ausbildung und Schulung und der Kontext, in dem das System eingesetzt werden soll, zu berücksichtigen.

Gewährleistung 
Hinsichtlich der Gewährung der Nutzung der Software sowie der Zurverfügungstellung von Speicherplatzes gelten die Gewährleistungsvorschriften des Mietrechts ( §§ 535 ff. BGB).
Der Kunde hat EcomTask jegliche Mängel unverzüglich anzuzeigen.
Die Gewährleistung für nur unerhebliche Minderungen der Tauglichkeit der Leistung wird ausgeschlossen. Die verschuldensunabhängige Haftung gem. § 536a Abs. 1 BGB für Mängel, die bereits bei Vertragsschluss vorlagen, ist ausgeschlossen.
 
Haftung
Die Parteien haften unbeschränkt bei Vorsatz, grober Fahrlässigkeit sowie bei schuldhafter Verletzung von Leben, Körper oder Gesundheit.
Unbeschadet der Fälle unbeschränkter Haftung gemäß Ziffer 8.1 haften die Parteien einander bei leicht fahrlässiger Pflichtverletzung nur bei Verletzung wesentlicher Vertragspflichten, also Pflichten, deren Erfüllung die ordnungsgemäße Durchführung des Vertrages überhaupt erst ermöglicht oder deren Verletzung die Erreichung des Vertragszwecks gefährdet und auf deren Einhaltung die andere Partei regelmäßig vertrauen darf, allerdings beschränkt auf den bei Vertragsschluss vorhersehbaren, vertragstypischen Schaden.
Die vorstehenden Haftungsbeschränkungen gelten nicht für die Haftung nach dem Produkthaftungsgesetz sowie im Rahmen schriftlich von einer Partei übernommener Garantien.
Diese Ziffer 8 gilt auch zu Gunsten von Mitarbeitern, Vertretern und Organen der Parteien. 
 
Rechtsmängel; Freistellung
EcomTask gewährleistet, dass die Software keine Rechte Dritter verletzt. EcomTask wird dem Kunden von allen Ansprüchen Dritter wegen von ihm zu vertretender Schutzrechtsverletzungen im Zusammenhang mit der vertragsgemäßen Nutzung der Software auf erstes Anfordern hin freistellen sowie die Kosten einer angemessenen Rechtsverfolgung ersetzen. Der Kunde wird EcomTask unverzüglich über Ansprüche von Dritten, die diese aufgrund der vertragsgemäßen Nutzung der Software gegen ihn geltend machen, informieren und ihm sämtliche erforderlichen Vollmachten erteilen und Befugnisse einräumen, um die Ansprüche zu verteidigen.
Der Kunde sichert zu, dass die auf den Servern von EcomTask abgelegten Inhalte und Daten sowie dessen Nutzung und Bereitstellung durch EcomTask, nicht gegen geltendes Recht, behördliche Anordnungen, Rechte Dritter oder Vereinbarungen mit Dritten verstoßen. Der Kunde wird EcomTask von Ansprüchen, die Dritte aufgrund eines Verstoßes gegen diese Ziffer geltend machen, auf erstes Anfordern freistellen.
 
Vergütung und Zahlungsbedingungen; Preisanpassungen
Der Kunde hat monatlich eine monatliche Bereitstellungsgebühr in Höhe von 39 EUR sowie eine nutzungsabhängige Gebühr in Höhe von 0,99 EUR pro Buchungsvorgang, jeweils zuzüglich MwSt. in der jeweils anfallenden gesetzlichen Höhe, an EcomTask zu zahlen.
Buchungsvorgänge im vorstehenden Sinne sind jeweils: Terminbuchungen, Terminverschiebungen.
Die Rechnungsstellung erfolgt kalendermonatlich zum 10. des Folgemonats.
Die Zahlung ist im SEPA-Basis- oder SEPA-Firmen-Lastschriftverfahren möglich. Der Kunde ist verpflichtet, gegenüber EcomTask bei Vertragsschluss ein entsprechendes SEPA-Lastschriftmandat zu erteilen und für ausreichende Deckung des angegebenen Kontos Sorge zu tragen.
Der Einzug der Lastschrift erfolgt fünf Kalendertage nach Rechnungsstellung. Der Kunde hat dafür Sorge zu tragen, dass sein Konto zu diesem Zeitpunkt die erforderliche Deckung aufweist. Kosten, die aufgrund der Nichteinlösung oder der Rückbuchung einer Lastschrift entstehen, trägt der Kunde, soweit er die Nichteinlösung oder Rückbuchung zu vertreten hat.
EcomTask kann die Vergütung gemäß Ziffer 10.1 der allgemeinen Preisentwicklung, den Kosten für die Erbringung der vertraglichen Leistungen (z. B. nach Neueinführung oder Änderung von Steuern, anderen Abgaben oder sonstigen gesetzlichen Bestimmungen oder infolge eines Anstieges von Lohn-, Material-, Dienstleister- oder sonstigen Kosten) und/oder der aktuellen Preisliste für Neuverträge über den AI-Assistenten) anpassen. Die Anpassung wird frühestens 6 Wochen nach ihrer Ankündigung in Schriftform oder per E-Mail wirksam.
 
Vertragslaufzeit und Beendigung 
Der Vertrag wird auf unbestimmte Zeit geschlossen und kann von beiden Parteien mit einer Frist von vier Wochen zum Monatsende gekündigt werden.
Das Recht zur fristlosen Kündigung aus wichtigem Grund bleibt unberührt.
Die Kündigung bedarf in jedem Fall der Schriftform.
EcomTask wird sämtliche auf seinen Servern verbleibenden Daten des Kunden 30 Tage nach Beendigung des Vertragsverhältnisses unwiederherstellbar löschen. Ein Zurückbehaltungsrecht oder Pfandrechte an den Daten zugunsten von EcomTask bestehen nicht.   
 
Datenschutz; Geheimhaltung; Referenzkunde
Die Parteien werden die für sie jeweils geltenden anwendbaren datenschutzrechtlichen Bestimmungen einhalten.
Soweit EcomTask im Auftrag des Kunden personenbezogene Daten verarbeitet, gilt vorrangig der in der Anlage 2 beigefügte Auftragsverarbeitungsvertrag gemäß Artikel 28 DSGVO.
EcomTask verpflichtet sich, über alle vertraulichen Informationen (einschließlich Geschäftsgeheimnissen), die EcomTask im Zusammenhang mit diesem Vertrag und dessen Durchführung erfährt, Stilschweigen zu bewahren und diese nicht gegenüber Dritten offenzulegen, weiterzugeben oder auf sonstige Art zu verwenden. Vertrauliche Informationen sind dabei solche, die als vertraulich gekennzeichnet sind oder deren Vertraulichkeit sich aus den Umständen ergibt, unabhängig davon, ob sie in schriftlicher, elektronischer, verkörperter oder mündlicher Form mitgeteilt worden sind. Die Geheimhaltungsverpflichtung gilt nicht, soweit EcomTask gesetzlich oder aufgrund bestands- bzw. rechtskräftiger Behörden- oder Gerichtsentscheidung zur Offenlegung der vertraulichen Information verpflichtet ist. EcomTask verpflichtet sich, mit allen Mitarbeitern und Subunternehmern eine den vorstehenden Absatz inhaltgleiche Regelung zu vereinbaren.
Ziffer 12.3 gilt nicht im Verhältnis zwischen EcomTask und der TimeGlobe GmbH, soweit es sich um Informationen handelt, die für die Einrichtung und den Betrieb der Software und ihre Anbindung an den TimeGlobe-Kalender notwendig sind und daher von EcomTask und der TimeGlobe GmbH ausgetauscht werden.
Der Kunde kann während der Dauer dieses Vertrags von EcomTask als Referenzkunde genannt werden. Die Angabe kann dabei auch online auf der Unternehmenswebseite von EcomTask und einschließlich der Nennung der Geschäfts-/Salonbezeichnung und ggf. des Firmenlogos des Kunden erfolgen.

Schlussbestimmungen
Sollten einzelne Regelungen dieses Vertrags unwirksam oder nicht durchführbar sein, bleibt die Wirksamkeit der übrigen Regelungen hiervon unberührt. Die Parteien werden solche Regelungen durch wirksame und durchführbare Regelungen ersetzen, die dem Sinn und wirtschaftlichen Zweck sowie dem Willen der Parteien bei Vertragsschluss möglichst gleichkommen. Entsprechendes gilt im Falle einer Vertragslücke.
Mündliche oder schriftliche Nebenabreden zu diesem Vertrag bestehen nicht. Änderungen dieses Vertrags und seiner Anlagen bedürfen der Schriftform.
Es gilt deutsches Recht unter Ausschluss der kollisionsrechtlichen Bestimmungen und des Übereinkommens der Vereinten Nationen über Verträge über den internationalen Warenverkauf vom 11.4.1980 (UN-Kaufrecht).
Ausschließlicher Gerichtsstand für alle Streitigkeiten aus oder im Zusammenhang mit diesem Vertrag ist Wiesbaden.
 `;
}; 