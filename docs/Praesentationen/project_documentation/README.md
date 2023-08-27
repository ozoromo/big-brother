# SoSe 23 Big Brother - Projektdokumentation

## Einleitung und Zielsetzung
Dieses Projekt wurde im Rahmen des Programmierpraktikums 
"moderne verteilte Anwendungen" absolviert. Ziel war es die Funktionalitäten
der webbasierten Anwendung vom Projekt "big brother 2021" zu erweitern. Unser
Ziel war es:

- weitere Zulassungskontrollalgorithmen,
- Gestenerkennung und
- Lehrvideoanalyse zu implementieren. 

Wir haben außerdem vor gehabt die Datenbank des vergangenen
Jahres noch flexibler mit MongoDB zu gestalten.

## Gruppenaufteilung
Um diese Ziele zu erreichen haben wir uns in Untergruppen aufgeteilt:

- **Datenbank**: Regelt implementation der Datenbank.
- **Logik**: Implementiert weitere Algorithmen, welche in unseren Zielen stehen.
Aufgrund der Komplexität dieser Aufgabe haben wir diese Gruppe nochmals in 
Untergruppen unterteilt:
    - **FnG** (engl. face and gesture): Diese Gruppe implementiert die Gesichts und
    Gestenerkennung.
    - **eduVid** (engl. educational videos): Diese Gruppe implementiert das 
    Analysieren von Lehrvideos
- **Frontend**: Diese Gruppe regelt die Webanwendung.

Um die Kommunikation und Zusammenarbeit in den Gruppen einfacher zu gestalten,
haben wir uns dazu entschieden, dass jede Untergruppe einen
verantwortliches Mitglied hat, welches dafür sorgt, dass die Schnittstellen,
welche von den anderen Nutzer genutzt werden, klar definiert sind. Dies soll
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
welche nicht so strikt strukturiert werden muss, wie SQL. Hierbei wird
die Datenbank so strukturiert, dass sich Anfragen effizienter bearbeiten lassen.
Bei herkömmlichen Datenbanken nimmt man in der Regel nicht viel Rücksicht auf die 
spezifischen/oft vorkommenden Anfragen der Datenbank beim Erstellen dessen,
weshalb Anfragen viele Tabellen mit Joins verknüpfen müssen, welche unnötigen
overhead verursachen könnten. Da wir das Projekt in Zukunft oft mit neuen
Ideen erweitern wollen, sien es sinnvoll eine flexiblere Datenbank aufzustellen.

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
Resourcen zu gruppieren. Man kann sich das so vorstellen, wie eine
Ordnerstruktur in einem Betriebssystem. Diese könnte auch genutzt werden, um
eine hierarchische Ordnerstruktur zu erstellen.
- `login_attempt`: Hier werden die Anmeldeversuche der Nutzer gespeichert.
Falls diese nicht erfolgreich sind, d.h. das Gesichtserkennungsbild
(also Passwort) wurde nicht erkannt, so ist der Eintrag `login_suc` auf *falsch*
gesetzt. Falls die Anmeldung erfolgreich war, wo ist `login_suc` auf *wahr*
gesetzt, wobei die ID der Resource, die zum erfolgreichen Anmelden geführt hat
in dem Feld `success_res_id` abgespeichert wird. Diese kann später abgerufen 
werden. Die `success_res_type` beschreibt den Typ der Ressource, welche zum
Erfolgreichen anmelden geführt hat. Wir nutzen in unserem System nur einen
Typ, jedoch kann man in Zukunft auch Resourcen, wie ein Video stream oder 
ähnliches nutzen.
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

In der dritten Phase des Projektes haben wir uns Gedanken über Nebenläufige
Datenbankzugriffe gemacht.
Da MongoDB automatisch die Daten, auf die Zugegriffen werden blockiert,
mussten wir hierbei nicht sehr viel machen. In dieser Phase haben wir
außerdem einige Funktionalitäten für andere Gruppen implementiert, falls diese
etwas in der Datenbank ablegen mussten. Dazu gehören:

- speichern von Videos mit zusätzlichen Informationen
- löschen von Videos
- aktualisieren von encodings
- und andere Hilfsfunktionen

Am Anfang des Projektes viel es etwas schwer den anderen Gruppen zu zeigen,
wie unsere Schnittstellen genutzt werden sollten. Hierzu haben wir zunächst
eine automatische Dokumentation aus dem *Docstring* erstellt. Diese Dokumentation
hat jedoch nicht genügend verdeutlicht, wie die Methoden miteinander genutzt werden sollen.
Dies haben wir gelöst, indem wir neben der Dokumentation auch noch Beispielcode
den anderen Gruppen gegeben wurde. Diesen Beispielcode haben wir in unseren
Tests implementiert, damit in Zukunft durch die automatischen Tests die
Korrektheit (zumindest teilweise) bestätigt werden kann.

Die Struktur der Datenbank ist in dem UML-Diagramm ersichtlich.

![UML database management](./images/classes_database_management.png)

Die Komponenten mit ihrer Bedeutung wird nun kurz erläutert:

- Exceptions: Wir haben zwei *exceptions* eingeführt, um Fehler besser 
beschreiben zu können.
- `BaseDatabase`: Hier sind die wesentlichen Funktionen für die 
Benutzerverwaltung implementiert. Diese Klasse fungiert als Fundament der
anderen zwei Klassen, die in den folgenden Stichpunkten erkläutert werden.
- `PictureDatabase`: Diese Klasse stellt die Funktionaliät bereit Bilder
in der Datenbank zu speichern und aufzurufen.
- `VideoDatabase`: Diese Klasse stellt die Funktionaliät bereit Videos
in der Datenbank zu speichern und aufzurufen. Intern wird ein anderer
Mechanismus genutzt als beim abspeichern der Bilder, da Bilder generell 
deutlich weniger Speicherplatz benötigen als Videos.

## Logik
Bei unserer Suche nach Möglichkeiten um Gesichter zu erkennen,
haben wir uns parallel im Internet als auch in den Ergebnissen 
der letzten Semester des Programmierpraktikums umgeschaut. 

Während man versucht hatte den Code aus den letzten Jahren zum Laufen
zu bekommen (nicht gelungen), wurde man schnell fündig bei einem
Youtube Kanal „Murtaza’s Workshop – Robotics and AI“ und paar anderen
interessanten Artikeln. Zu den Artikeln später mehr.

Für die Umsetzung der Gesichtserkennung wurde das python package
"face-recognition" benutzt ähnlich auch wie von Murtaza erklärt. 
Der Grund dafür war die Einfachheit der Nutzung und dadurch 
der besser überschaubare Code. Zudem bekommt man eine hohe 
Treffsicherheit von 99.38% hin. 

face-recognition ist eine Open-Source-Bibliothek, die auf der Grundlage
von OpenCV entwickelt wurde und auf der Gesichtserkennungstechnologie
von dlib basiert. Sie ermöglicht die Erkennung und Analyse von Gesichtern
in Bildern und Videos.

Die Gesichtserkennungstechnologie von dlib basiert auf dem 2017 veröffentlichten
"Histogram of Oriented Gradients for Human Detection" (HOG)-Feature-Extractor und 
dem "Linear Support Vector Machines" (SVM)-Klassifikator. 
Diese Methode wurde von Navneet Dalal und Bill Triggs in ihrer 
Veröffentlichung "Histograms of Oriented Gradients for Human Detection" vorgestellt.

Die dlib-Bibliothek verwendet eine Kombination aus HOG-Features und 
SVM-Klassifikation, um Gesichter in Bildern zu erkennen. 
Der HOG-Algorithmus basiert auf der Idee, dass das Erscheinungsbild 
eines Objekts durch die Verteilung von Gradienten oder Kanteninformationen
beschrieben werden kann. Es werden Histogramme der Gradientenrichtungen 
erstellt und diese Histogramme dienen als Features für den Klassifikator.

Der SVM-Klassifikator wird trainiert, um zwischen Gesichts- und 
Nicht-Gesichtsregionen zu unterscheiden. Dafür werden positive Beispiele
von Gesichtern und negative Beispiele von Nicht-Gesichtern verwendet. 
Der SVM-Klassifikator lernt dann, diese beiden Klassen zu unterscheiden 
und kann anschließend auf neue Bilder angewendet werden, um Gesichter zu erkennen.

Die dlib-Bibliothek stellt auch eine vortrainierte Gesichtserkennungsmodell-Datei bereit,
die mit dem HOG-Feature-Extractor und dem SVM-Klassifikator trainiert wurde. 
Dieses Modell wird verwendet, um Gesichter zu erkennen und 
kann mit der Funktion `dlib.get_frontal_face_detector()` abgerufen werden.

face-recognition arbeitet mit encodings von den Bildern, d.h. aus einem
rgb Bild zum Beispiel jpeg oder pdf werden numpy arrays in Form von Matrizzen erstellt.
Dazu wird die Methode `face_recognition.face_encodings()` benutzt. 
Der Rückgabewert dieser Funktion ist dann das numpy array des Bildes. 
Die Berechnung dieser numpy arrays ist allerdings rechenlastig und wird
bei jedem Bild erneut gemacht, weswegen wir eine Möglichkeit gefunden haben
eben diese encodings zu cashen. Das geschieht in encodings_class.py.

TODO: die anderen methoden noch erläutern. 
## eduVid (engl. educational videos)

### Projektziele und ihre Erreichung
Wir nutzen folgende tools, um die Videoanalyse umzusetzen:

- `faster-whisper` für das umwandeln von Sprache zu Text.
- Das vortrainierte model `mdeberta-v3-base-squad2` von *hugging face*, um
die Fragen zu beantworten, welche man zum video hat.
- `MoviePy` für das bearbeiten des Videos

### Beschreibung des Algorithmus
Im folgenden wird der Verlauf des Programms kurz beschrieben:

1. Nutzer lädt ein Video in mp4-format hoch
2. Die Audio wird von der mp4-Datei extrahiert und in dem wav-format
gespeichert.
3. Die Spracherkennung wird genutzt, um die Audiodatei in Text zu konvertieren.
4. Das extrahierte Transkript wird verarbeitet, damit das Programm den Kontext
zwischen den Sätzen versteht.
5. Daraufhin wird das Model genutzt, um die Frage zu beantworten. Es wird 
außerdem bestimmt, wann diese Antwort im Video erwähnt wird.

![UML database management](./images/diagram.png)

### Auftretene Schwierigkeiten

- Spracherkennung: Die Antworten auf die Fragen werden in dem Kontext gesucht,
welche von der Spracherkennung generiert wurden. Beim Testen ist aufgefallen,
dass jeder Spracherkennungalgorithmus seine schwächen hat und manche Wörter
nicht korrekt erkennt. Dies beeinflusst die Antwort auf Fragen. Während
des Arbeitens sind uns einige Teile des Algorithmus aufgefallen, welche wir
in Zukunft optimieren könnten:
    - der längste Prozess des Algorithmus ist die Spracherkennung. Wenn man
    den Algorithmus verschnellern möchte, sollte man einen Weg finden diesen
    zu verschnellern ohne einen zu starken Preis bezüglich der Korrektheit zu
    zahlen.
- Antworten der Algorithmen sind keine wohl-formilierten Sätze. Dies könnte
die Antwort auf Definitionsfragen (z.B. Wie ist [...] definiert?) sehr
unverständlich machen. Der Algorithmus beantwortet Fragen oft mit einzelnen
Schlüsselfwörtern.
- Der Algorithmus hat einige Schwierigkeiten grammatikalische Details einer
Sprache ausfindig zu machen. Manchmal sind Zeitformen bei der Beantwortung
der Fragen relevant. Diese werden nicht berücksichtigt, wodurch die Antwort
auf eine Frage falsch sein könnte.

### Empfehlungen fuer weiteres Vorgehen
- Spracherkennung:
    - Automatische benchmarktests können genutzt werden, um die Bewertung der
    Spracherkennung zu vereinfachen.
    - Eventuell falsch erkannte Wörter könnten versucht werden zu identfizieren.
    Daraufhin könnte versucht werden diese durch das wahrscheinlichste Wort, 
    statt dem im Kontext sinnfreien Wort zu ersetzen. Falls der Sprecher
    undeutlich Spricht kann dies zu einer höheren Genauigkeit der entgültigen
    Antwort beitragen.
    - In bestimmten Videos werden vielleicht bestimmte Fachwörter genutzt.
    Es wäre nützlich, falls unser Programm diese Fachwörter verstehen könnte.
- Slide-Extraktion: Wir haben auch daran gearbeitet das Bildmaterial des Videos
zu verarbeiten, um die Antwort genauer zu machen, um den Kontext des Videos
besser zu verstehen. Es wurde bereits ein Ansatz in dem eduVid-Ordner 
(unter /src/eduVid/handle\_presentation(unused)) implementiert. Dieser Ansatz
kann in Zukunft weiter geführt werden.
- Ein weitere Schritt wäre es zu erkennen, wenn das Thema des videos geändert
wird. Momentan haben fordern wir jedoch den Nutzer dazu auf eine Datei bereit
zu stellen, die Aussagt, wann ein Thema gewechselt wird. Jedes Thema hat
hierbei eine überschrift und ist entsprechend mit Schlüsselwörtern
gekennzeichnet.
  
## Frontend
### Webanwendung
Wir haben uns dazu entschieden das Flask-Framework von dem vorherigen Projekt
weiter zu nutzen. Flask ist möglichst einfach gehalten und besitzt
im Vergleich zu anderen Webframeworks keine unnötigen Funktionen. Von anderen
Bibliotheken abgedeckte Funktionen, werden nicht in Flask umgesetzt und lassen
sich über die bestehenden Bibliotheken integrieren.

### Ordnerstruktur
Wir haben uns dazu entschieden Bluprints zu benutzen. Die Klassen `user.py`,
`utils.py`, `__init__.py` & `user_manager.py` waren zu unübersichtlich während der
Bearbeitung. Blueprints bietet eine übersichtlichere Struktur im Projekt. Die Inhalte
der Klassen wurden in die Ordner `logic`, `login`, `main` & `users` unterteilt.
Der Entwicklungsprozess kann gezielter und effektiver gestaltet werden, wenn er
eine bestimmte Struktur hat.

### Milestone 1
Als ersten Meilenstein haben wir uns gesetzt den Code vom Team21 zu analysieren
und zu verstehen, sowie die Website zu überarbeiten. Um die Website zu
überarbeiten, musste jedoch der Zugriff auf die Website hergestellt werden.
Dafür wurden sämtliche Requirements mit den dafür vorgesehenen Versionen
heruntergeladen. Dabei muss man auf die richtige Python Version (Python 3.10.2)
achten, damit alle Requirements heruntergeladen werden können. Des Weiteren ist
aufgefallen, dass es obsolete Requirements gab, die entfernt wurden. Dies war
ein kleines Hindernis, da einige Probleme mit der Umstellung ihrer Python
Versionen hatten. Anschließend wurde der Vorgang in der „ReadMe“ Datei
dokumentiert.

### Milestone 2
Die Aufgaben wurden innerhalb der Gruppe aufgeteilt. Es wurden fehlende Routes,
wie „sign up with photo“ und „sign in with photo“, hinzugefügt und manuell
getestet. Zusammen mit dem Backend und Logik Team wurden die Bugs gefixt. So wurden
beispielsweise einige Variablen falsch übernommen. Wir haben bewusst mit den
anderen Teams die Bugs gefixt, da die zu implementierenden Inhalte in ihren
Themenfeldern waren, und sie dementsprechend schnell die gefundenen Fehler
beheben konnten. Des Weiteren haben wir uns für ein neues Design der Website
entschieden, um die Seite visuell attraktiver für den User zu gestalten.
Während dieser Phase gab es Schnittstellen Probleme zur Registrierung und
Anmeldung mit der Gesichtserkennung („FaceRecognition“).

### Milestone 3
So haben wir beschlossen in der Dritten Phase die Probleme bezüglich der
Gesichtserkennung zu beheben. Bei der Anmeldung mit Kamera gab es nun einen
Countdown und nach Ablauf des Countdowns wird ein Bild gemacht, welcher
automatisch heruntergeladen wird. Für EduVid wurde vorerst ein Platzhalter
implementiert, in der man lediglich ein Video mit einem Titel hochladen kann. 
Des Weiteren haben wir das gesamtes Team SoSe2023 auf der Webseite verewigt,
wie es das SoSe2021 vor uns gemacht hat.

Der GPU-Server wurde konfiguriert. Das Team hatte anfangs Probleme mit dem
Konfigurieren des Servers, weswegen wir uns gemeinsam der Aufgabe gewidmet
haben. Um den Server zu deployen haben wir angefangen einen Dockerfile zu
erstellen. Dieser wurde nicht ganz fertig bis zum präsentieren des 3.
Milestones. 

### Nach dem Milestone 3
Nach dem 3. Milestone haben wir zunächst den Docker-Container zum laufen
bekommen. Daraufhin haben wir die Gesichtserkennung fertig gestellt. Das
Vergleichen des live Images mit den Bildern aus der Registrierung, welche im
Backend gespeichert wird, war ein Erfolg. Die Idee in diesem Vorgang das Bild
sichtbar für den User zu downloaden, wurde nicht übernommen.

Im History werden die Bilder, die zur Anmeldung genutzt werden aufgelistet.
Das Datum der Anmeldung wurde neben den "Anmeldungsbildern" implementiert.

Für die Gestenerkennung hatten wir uns überlegt, diese ebenfalls für die Anmeldung
zu nutzen. Die Templates und Routes wurden dafür erstellt. Doch wir kamen zu dem
Entschluss, dass die Anmeldung mit einer Geste keine Sicherheit gewährleistet.
So wurde die Gestenerkennung für den User nach der Anmeldung implementiert.
Dabei sind 2 Screens zu sehen. Auf dem linken Screen ist die live Cam, 
bei der Fotos in einem bestimmten Zeitintervall erstellt werden. Bilder werden auf
den rechten Screen übertragen und angezeigt. Um den Vorgang in Echtzeit zu
realisieren nutzen wir Socket.IO.

Nach dem 3. Milestone und nach dem die EduVid Logik fertig war, wurde die 2.
Ausbaustufe von EduVid implementiert. Zusätzlich zum Video Upload muss nun eine
json Datei, welche passende Time-Stamps für das Video enthält, und ein Frage zu
dem Video angegeben werden. Nach Upload werden passende Antworten gefunden und
1 oder mehere Time-Stamps zu diesen erstellt. Auf der neuen Seite stehen die
Time-Stamps aus der json Datei so wie die aus der Logik Funktion erstellten
Time-stamps zur verfügung, wie auch eine Antwort auf die gestellte Frage. Die
json Datei muss einen Eintrag "time-stamps" enthalten, welcher Objekte der Form
`{ "label": <time in seconds> }` enthalten muss.
Zusätzlich wurden Videounabhängige Time-Stamp Buttons erstellt, mit welchen
man an bestimmte Stellen im Video springen kann. 

Beispiel einer Time-Stamps JSON Datei:
```javascript
{
	"time-stamps": [
		{"Intro": 0.0},
		{"Core Idea": 10.0},
		{"Next Steps": 30.0},
		{"Advanced": 300.0},
		{"Conclusion": 500.0},
		{"Outro": 700.0}
	]
}
```

#### Anmerkung zu EduVid:
Beim verlassen der Seite läuft im Backend die Logik zur Video verarbeitung
weiter, hier könnte man in einer weiteren Ausbaustufe mittels einer socket
connection überprüfen, ob man sich noch auf der Seite befindet (auf das Video
ergebnis wartet) und ggf. die Verarbeitung frühzeitig abbrechen. Ähnlich wird
dies bereits bei der Gestenerkennung umgesetzt.
