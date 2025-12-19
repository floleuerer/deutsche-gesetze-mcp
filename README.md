# Deutsche Gesetze MCP Server

Dieser Server implementiert das [Model Context Protocol (MCP)](https://modelcontextprotocol.io), um deutschen Gesetzestexte für LLMs (Large Language Models) bereitzustellen. Er ermöglicht es KI-Assistenten, gezielt nach Gesetzen zu suchen und spezifische Paragraphen abzurufen.

Die Gesetzestexte werden aus Markdown-Dateien geparst, die dem Format des [Bundestag/gesetze](https://github.com/bundestag/gesetze) Repositories entsprechen (Hinweis: Dieses Repository ist veraltet und dient nur zu Demozwecken).

## Funktionen

*   **Gesetze auflisten & suchen**: Durchsuchen der verfügbaren Gesetze (z.B. BGB, StGB, HGB).
*   **Volltextsuche**: Suche nach Begriffen in den Gesetzestexten.
*   **Paragraphen abrufen**: Abruf des Volltextes spezifischer Paragraphen (inkl. Absätze).
*   **Flexible Datenquellen**: Laden der Gesetze aus einem lokalen Ordner oder direkt von GitHub.

## Installation

### Lokal

1.  **Repository klonen:**
    ```bash
    git clone https://github.com/floleuerer/deutsche-gesetze-mcp.git
    cd deutsche-gesetze-mcp
    ```

2.  **Abhängigkeiten installieren:**
    Es wird empfohlen, eine virtuelle Umgebung zu verwenden (z.B. `venv` oder `conda`).
    ```bash
    pip install -r mcp/requirements.txt
    ```

### Docker (Empfohlen)

Die Docker-Version klont automatisch das gesamte [Bundestag/gesetze](https://github.com/bundestag/gesetze) Repository (veraltet, nur Demo) in das Image, sodass alle Gesetze sofort lokal verfügbar sind.

1.  **Image bauen:**
    ```bash
    docker build -t deutsche-gesetze-mcp .
    ```

2.  **Container starten:**
    ```bash
    docker run -p 8001:8001 deutsche-gesetze-mcp
    ```

## Datenvorbereitung

Das Projekt enthält im Ordner `prepare_data` Skripte, um aktuelle Gesetzestexte direkt von [www.gesetze-im-internet.de](https://www.gesetze-im-internet.de) herunterzuladen und für den Server aufzubereiten.

1.  **Skript ausführen:**
    ```bash
    cd prepare_data
    ./prepare_gesetze_im_internet.sh
    ```
    Dies lädt die Gesetze herunter, entpackt sie und konvertiert sie in das benötigte Format.

## Konfiguration

Die Konfiguration erfolgt über Umgebungsvariablen oder eine `.env` Datei. Die Einstellungen werden in `mcp/config.py` definiert.

| Variable | Beschreibung | Standardwert |
| :--- | :--- | :--- |
| `LOAD_FROM_FOLDER` | Pfad zu einem lokalen Ordner mit Gesetzes-Markdown-Dateien. | `/app/gesetze/` |
| `LOAD_FROM_GITHUB` | JSON-Liste von Gesetzeskürzeln, die von GitHub geladen werden sollen (überschreibt `LOAD_FROM_FOLDER`, wenn gesetzt). | `None` |
| `MIN_PARAGRAPHS` | Minimale Anzahl an Paragraphen, damit ein Gesetz geladen wird. | `5` |

**Beispiel `.env` Datei:**
Um Gesetze direkt von GitHub zu laden (z.B. BGB und StGB):
```env
LOAD_FROM_GITHUB='["BGB", "StGB"]'
LOAD_FROM_FOLDER=
```

Um lokale Dateien zu nutzen (angenommen, sie liegen in `./gesetze`):
```env
LOAD_FROM_FOLDER=./gesetze
```

## Nutzung

### Server starten

Der Server kann direkt über Python gestartet werden. Er nutzt `FastMCP` und stellt standardmäßig einen HTTP-Server auf Port 8001 bereit.

```bash
python mcp/server.py
```

### Tests

Die Tests können mit `pytest` ausgeführt werden. Um die Tests zu starten, muss der `mcp` Ordner im Python-Pfad liegen:

```bash
PYTHONPATH=mcp python3 -m pytest mcp/tests
```

### Verfügbare Tools

Der Server stellt folgende MCP-Tools zur Verfügung:

1.  **`get_lawlibrary(law: str | None)`**
    *   Listet verfügbare Gesetze auf.
    *   Parameter `law`: (Optional) Suchbegriff oder Kürzel, um die Liste zu filtern (z.B. "BGB").
    *   Gibt eine JSON-Liste der gefundenen Gesetze zurück.

2.  **`get_paragraph(law: str, paragraph: str)`**
    *   Ruft den Inhalt eines Paragraphen ab.
    *   Parameter `law`: Das Kürzel des Gesetzes (z.B. "BGB").
    *   Parameter `paragraph`: Die Nummer des Paragraphen (z.B. "1", "14a").
    *   Gibt den Text des Paragraphen (und ggf. spezifische Absätze) zurück.

3.  **`search_laws(query: str, laws: list[str] | None)`**
    *   Volltextsuche über alle oder ausgewählte Gesetze.
    *   Parameter `query`: Der Suchbegriff (z.B. "Schadensersatz", "Kündigung").
    *   Parameter `laws`: (Optional) Liste von Gesetzeskürzeln zur Einschränkung der Suche (z.B. `["BGB", "HGB"]`).
    *   Gibt eine Liste von Treffern mit Paragraphen und Textausschnitten zurück.

### Verwendung mit MCP-Clients

Dieser Server kann mit jedem MCP-kompatiblen Client verbunden werden. Da er als HTTP-Server (SSE) läuft, muss der Client entsprechend konfiguriert werden, um sich mit `http://localhost:8001/mcp` zu verbinden.

Ein Beispiel für die Integration in einen KI-Agenten findest du im Ordner [google-adk-agent](./google-adk-agent), der das **Google Agent Development Kit (ADK)** nutzt.

## Datenformat

Der Parser erwartet Markdown-Dateien, wie sie im Projekt [bundestag/gesetze](https://github.com/bundestag/gesetze) (veraltet, nur Demo) verwendet werden. Die Struktur sieht typischerweise so aus:

```markdown
---
Title: Bürgerliches Gesetzbuch
jurabk: BGB
---

# § 1 Beginn der Rechtsfähigkeit

Die Rechtsfähigkeit des Menschen beginnt mit der Vollendung der Geburt.
...
```

## Lizenz

Siehe [LICENSE](LICENSE) Datei.
