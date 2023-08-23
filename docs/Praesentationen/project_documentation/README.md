# SoSe 23 Big Brother - Projektdokumentation

## Einleitung und Zielsetzung
Dieses Projekt wurde im Rahmen des Programmierpraktikums 
"moderne verteilte Anwendungen" absolviert. Ziel war es die Funktionalitäten
der webbasierten Anwendung vom "big brother 2021" zu erweitern. Unser Ziel
war es:
- weitere Zulassungskontrollalgorithmen
- Gestenerkennung 
- Lehrvideoanalyse
zu implementieren. Wir haben außerdem vor gehabt die Datenbank des vergangenen
Jahres noch flexibler mit MongoDB zu gestalten.

## Gruppenaufteilung
Um diese Ziele zu erreichen haben wir uns in Untergruppen aufgeteilt:
- Datenbank: Regelt implementation der Datenbank.
- Logik: Implementiert weitere Algorithmen, welche in unseren Zielen stehen.
Aufgrund der Komplexität dieser Aufgabe haben wir diese nochmals in 
Untergruppen unterteilt:
    - FnG (engl. face and gesture): Diese Gruppe implementiert die Gesichts und
    Gestenerkennung.
    - eduVid (engl. educational videos): Diese Gruppe implementiert das 
    analysieren von Lehrvideos
- Frontend: Diese Gruppe regelt die Webanwendung.

Um die Kommunikation und Zusammenarbeit in den Gruppen nicht zu kompliziert 
schwierig machen, haben wir uns dazu entschieden, dass jede Untergruppe einen
verantwortliches Mitglied hat, welches dafür sort, dass die Schnittstellen,
welche von den anderen Nutzer genutzt werden klar definiert sind. Dies soll
mit Tests und Maßstäben (engl. benchmarks) sichergestellt werden. Die Tests
sind vorallem wichtig, damit zukünftig an diesem Projekt arbeitende Gruppen
unseren Code besser verstehen können und Schwierigkeiten beim Debuggen
neu strukturieren können. Zusammengefasst haben Tests das Ziel
- den Code besser zu erklären,
- Workflows zu verdeutlichen,
- debugging zu vereinfachen und
- innere Logik von Funktionen und Methoden abändern zu können, ohne Angst 
haben zu müssen die Schnittstellen unbewusst kaputt zu machen.

## Datenbank
Wie in der Einleitung bereits erwähnt, haben wir uns dazu entschieden die
Datenbank in MongoDB zu implementieren. Dies ist eine NoSQL-Datenbank,
welche nicht so strikt strukturiert werden muss, wie SQL. Hierbei werden die
Inhalte in der Datenbank nicht normalisert, sondern so Erstellt, dass die
Anfragen an die Datenbank schneller bearbeitet werden kann. Bei herkömmlichen
Datenbanken nimmt man in der Regel nicht viel Rücksicht auf die 
spezifischen/oft vorkommenden Anfragen der Datenbank beim Erstellen dessen,
weshalb Anfragen viele Tabellen mit Joins verknüpfen müssen, welche unnötigen
overhead verursachen könnten. Da wir das Projekt in Zukunft oft mit neuen
Ideen erweitern wollen, wollte die Datenbank auf flexibler sein.

Hierzu haben wir ein zunächst ein Datenbankschema entwickelt. Hierbei nutzen wir
eine Notation, welche ähnlich zu der ER-Model-Notation ist, um
die Struktur leichter verständlich zu machen:
![DB schema image](./images/db_schema.png)

Die Entitäten in diesem Modell sind *Collections* in MongoDB, wobei deren
Inhalt *Documents* sind. Wir erklären die Entitäten, einige Beziehungen
zueinenander und unsere Designentscheidungen im Folgenden kurz:
- `resource`: Dies ist im eine Resource in unserem System. Wir nutzen dies,
um beispielsweise Bilder zu speichern.
- `resource_context`: Dies ermöglicht uns die IDs von den verschiedenen 
Resourcen zu gruppieren. Man kann sich das so ähnlich vorstellen, wie eine
Ordnerstruktur in einem Betriebssystem. Diese könnte auch genutzt werden, um
eine hierarchische Ordnerstruktur zu erstellen. In unserem Projekt nutzen wir
dies lediglich, um Resourcen zu gruppieren.
- `login_attempt`: Hier werden die Anmeldeversuche der Nutzer gespeichert.
Falls diese nicht erfolgreich sind, d.h. das Gesichtserkennungsbild
(also Passwort) wurde nicht erkannt, so ist der Eintrag `login_suc` auf *falsch*
gesetzt. Falls die Anmeldung erfolgreich war, wo ist `login_succ` auf *wahr*
gesetzt, wobei die ID der Resource, die zum erfolgreichen Anmelden geführt hat
in dem Feld `success_res_id` abgespeichert wird. Diese kann später abgerufen 
werden. Die `success_res_type` beschreibt den Typ der Ressource, welche zum
Erfolgreichen anmelden geführt hat. Wir nutzen in unserem System nur einen
Typ, jedoch kann man in Zukunft auch Resourcen, wie ein Video stream oder 
ähnlichen nutzen.
- `user`: Speichert wichtige Nutzerdaten. Hierbei werden sogenannte "encodings"
für jeden Nutzer abgespeichert. Diese enthalten Daten des Gesichts des Nutzers
und werden für den Gesichtserkennungsalgorithmus benötigt. Da diese Daten so
groß sind und man diese nicht jedes mal von der Datenbank in den Hauptspeicher
laden möchte, wenn man nur den Benutzernamen einer `_id` abfragen möchte,
was in unserer Anwendung recht häufig passiert, speichern wir nur ab, wo man
das Encoding bei den Resourcen finden kann.

Das Implemplementieren geschah in der ersten und zweiten Phase des Projekts
wie geplant. Hierbei mussten wir besonders darauf achten, dass wir die
Schnittstellen der alten Datenbank beibehalten. Durch unsere Implementierung
und kleine Seiteneffekte ist in dieser Phase des Projektes einiges an Code
am Frontend kaputt gegangen. Daraufhin haben wir mehr tests entwickelt, um
die unsere Schnittstellen besser für die Anwendungsfälle der anderen Gruppen
zu Testen. Hierbei hat es bei uns besonders geholfen, wenn eine Person
zuerst die Tests und Beschreibung (in Python den *Docstring*) für zu 
implementierenden Funktionalitäten geschrieben hat und eine andere Person 
die Funktionalitäten implementiert hat.

In der dritten Phase des Projektes haben wir versucht zu überlegen, was 
passieren könnte, wenn wir Nebenläufige Zugriffe auf die Datenbank haben.
Da MongoDB automatisch die Daten, auf die Zugegriffen werden blockiert,
mussten wir hierbei nicht sehr viel machen. In dieser Phase haben wir
außerdem einige Funktionalitäten für andere Gruppen implementiert, falls diese
etwas in der Datenbank ablegen mussten.

Am Anfang des Projektes viel es etwas schwer den anderen Gruppen zu zeigen,
wie unsere Schnittstellen genutzt werden sollten. Hierzu haben wir zunächst
eine automatische Dokumentation aus dem *Docstring* erstellt. Diese hab jedoch
nicht wirklich gezeigt, wie die Methoden miteinander genutzt werden sollen.
Dies haben wir gelöst, indem wir neben der Dokumentation auch noch Beispielcode
den anderen Gruppen gegeben wurde. Diesen Beispielcode haben wir in unseren
Tests implementiert, damit in Zukunft durch die automatischen Tests die
Korrektheit (zumindest teilweise) bestätigt werden kann.

Die Struktur der Datenbank ist in dem unteren UML-Diagramm ersichtlich:
![UML database management](./images/classes_database_management.png)
Die Komponenten mit ihrer Bedeutung wird nun kurz erläutert:
- Exceptions: Wir haben zwei *exceptions* eingeführt, um Fehler besser 
beschreiben zu können.
- `BaseDatabase`: Hier sind die wesentlichen Funktionen für die 
Benutzerverwaltung implementiert. Diese Klasse fungiert als fundament der
anderen zwei Klassen, die in den folgenden Stichpunkten erkläutert werden.
- `PictureDatabase`: Diese Klasse stellt die Funktionaliät bereit Bilder
in der Datenbank zu speichern und aufzurufen.
- `VideoDatabase`: Diese Klasse stellt die Funktionaliät bereit Videos
in der Datenbank zu speichern und aufzurufen. Intern wird ein anderer
Mechanismus genutzt als beim abspeichern der Bilder, da Bilder generell 
deutlich weniger Speicherplatz benötigen als Videos.

## Logik
Das Python-Paket "face-recognition" ist eine Open-Source-Bibliothek, 
die auf der Grundlage von OpenCV entwickelt wurde 
und auf der Gesichtserkennungstechnologie von dlib basiert. 
Sie ermöglicht die Erkennung und Analyse von Gesichtern in Bildern und Videos.

Die Gesichtserkennungstechnologie von dlib basiert auf dem 2017 veröffentlichten 
"Histogram of Oriented Gradients for Human Detection" (HOG)-Feature-Extractor 
und dem "Linear Support Vector Machines" (SVM)-Klassifikator. 
Diese Methode wurde von Navneet Dalal und Bill Triggs in ihrer Veröffentlichung
"Histograms of Oriented Gradients for Human Detection" vorgestellt.

Die dlib-Bibliothek verwendet eine Kombination aus HOG-Features und SVM-Klassifikation, 
um Gesichter in Bildern zu erkennen. Der HOG-Algorithmus basiert auf der Idee, 
dass das Erscheinungsbild eines Objekts durch die Verteilung von Gradienten 
oder Kanteninformationen beschrieben werden kann. Es werden Histogramme der 
Gradientenrichtungen erstellt und diese Histogramme dienen als Features für den Klassifikator.

Der SVM-Klassifikator wird trainiert, um zwischen Gesichts- 
und Nicht-Gesichtsregionen zu unterscheiden. Dafür werden positive Beispiele 
von Gesichtern und negative Beispiele von Nicht-Gesichtern verwendet. 
Der SVM-Klassifikator lernt dann, diese beiden Klassen zu unterscheiden 
und kann anschließend auf neue Bilder angewendet werden, um Gesichter zu erkennen.

Die dlib-Bibliothek stellt auch eine vortrainierte Gesichtserkennungsmodell-Datei bereit, 
die mit dem HOG-Feature-Extractor und dem SVM-Klassifikator trainiert wurde. 
Dieses Modell wird verwendet, um Gesichter zu erkennen 
und kann mit der Funktion `dlib.get_frontal_face_detector()` abgerufen werden.
