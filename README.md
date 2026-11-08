# MBStudio91 DAW

DAW che gira nel browser, con un generatore di loop integrato e il collegamento
al modello open source **ACE-Step 1.5** per generare musica da descrizione testuale.
Ispirata al flusso di lavoro di Sonura Studio, costruita interamente su librerie e
modelli con licenza permissiva.

> Prototipo `v0.1` — MBStudio91 · Piedmont Electronic Sound

## Cosa fa oggi

| Area | Funzioni |
|---|---|
| Arrangiamento | tracce multiple, clip con forma d'onda, trascinamento con griglia al battito (anche tra tracce), duplica, elimina, zoom |
| Trasporto | play/pausa/stop, loop senza interruzioni, metronomo, BPM, posizione in battute e secondi |
| Mixer | volume, panoramica, muto e solo per traccia, compressore e meter sul master |
| Generatore locale | batteria e basso (House, Techno, Trap, Breakbeat), accordi pad, arpeggi, riser, downlifter, impact; tonalità, scala e giro di accordi selezionabili |
| AI | generazione con ACE-Step 1.5 tramite la sua API REST |
| File | import WAV/MP3/FLAC/OGG (anche trascinando sull'arrangiamento), export del mix in WAV 16 bit 44,1 kHz |

Scorciatoie: `Spazio` play/pausa · `L` loop · `M` metronomo · `D` duplica clip · `Canc` elimina clip · `Alt` + trascina = senza griglia.

## Avvio rapido (solo DAW e generatore locale)

Serve solo Python 3.8 o superiore, nessuna installazione.

```bash
git clone https://github.com/<tuo-utente>/mbstudio91-daw.git
cd mbstudio91-daw
python serve.py
```

Apri **http://localhost:8080**. All'avvio viene generato un progetto demo di 8 battute in La minore.

## Generazione AI senza installare niente (Hugging Face)

Nella scheda **AI · ACE-Step** la sorgente predefinita è **Hugging Face**: la DAW usa la demo
pubblica [ACE-Step/Ace-Step-v1.5](https://huggingface.co/spaces/ACE-Step/Ace-Step-v1.5) tramite la
libreria ufficiale `@gradio/client` (caricata da jsDelivr). Basta aprire `index.html` con un doppio clic.

- Funzione chiamata: `/generation_wrapper` (Gradio 6.2). I parametri vengono letti dallo Space a ogni
  connessione e compilati per etichetta (Music Caption, Lyrics, BPM, Key, Audio Duration…); gli altri
  restano ai valori predefiniti dello Space.
- Lo Space usa GPU condivise (ZeroGPU): può esserci coda e c'è un limite giornaliero di minuti.
  Un token gratuito di Hugging Face (Settings → Access Tokens, tipo *Read*) alza il limite.
  Il token resta salvato solo nel browser.
- Non funziona dalla pagina pubblicata su Claude, che blocca i collegamenti a siti esterni.
- Se gli autori cambiano lo Space, la funzione può smettere di rispondere: in quel caso il campo
  **Space** permette di puntare a un duplicato (anche il tuo, creato con "Duplicate this Space").

## Lab: modelli che girano nel browser (solo studio)

> **Solo a scopo di studio.** YuE2 e MiniMax-Music3 sono rilasciati con licenze non commerciali.
> Per qualunque uso commerciale servono licenze a pagamento rilasciate dai rispettivi autori,
> non legate a MBStudio91. MBStudio91 non ottiene alcun guadagno da questo progetto, nemmeno dalla pubblicità.

La scheda **Lab** raccoglie i generatori che girano interamente nel browser con WebGPU, sulla scheda
video del computer, senza server e senza Python:

| Modello | Generatore | Download | Requisiti | Licenza |
|---|---|---|---|---|
| ACE-Step 1.5 | [shreyask/ace-step-webgpu](https://huggingface.co/spaces/shreyask/ace-step-webgpu) | ~2 GB | ~4 GB RAM libera, Chrome/Edge 113+, Safari 26+ | Apache 2.0 |
| YuE2 3B | [mrfakename/yue2-webgpu](https://huggingface.co/spaces/mrfakename/yue2-webgpu) | ~2,1 GB (q4) | WebGPU | CC BY-NC 4.0 |
| MiniMax-Music3 | [li-na.github.io/minimax-music3-webgpu](https://li-na.github.io/minimax-music3-webgpu/) | ~8 GB | 12–16 GB VRAM, Chrome 151+ con shader-f16 | MiniMax-Music3 Community License (non commerciale) |

- **Controlla la scheda video** verifica WebGPU, shader-f16, dimensione massima dei buffer e versione del browser.
  La memoria video totale non è leggibile dal browser: per i modelli grandi l'unica prova certa è avviarli.
- Il brano scaricato dal generatore si importa con **Scegli il file e importa**: la traccia riporta modello e
  licenza, e l'export del mix avvisa se contiene audio con licenza non commerciale.
- MiniMax richiede di dichiarare come generato dall'AI l'audio diffuso pubblicamente.

Fonti: [ACE-Step WebGPU](https://huggingface.co/spaces/shreyask/ace-step-webgpu/blob/main/README.md) ·
[YuE2 ONNX](https://huggingface.co/mrfakename/YuE2-3B-ONNX) ·
[MiniMax-Music3 WebGPU](https://huggingface.co/hyung778/minimax-music3-webgpu)

## Collegare ACE-Step 1.5 in locale (generazione AI sul tuo computer)

ACE-Step 1.5 gira in locale con meno di 4 GB di VRAM (GPU NVIDIA consigliata; supporta anche Mac con Apple Silicon).

```bash
# 1. installa ACE-Step 1.5 (vedi il README ufficiale per i dettagli della tua piattaforma)
git clone https://github.com/ace-step/ACE-Step-1.5.git
cd ACE-Step-1.5
# ... installazione dipendenze secondo la guida ufficiale ...

# 2. avvia il server API (porta 8001)
python -m acestep.api_server

# 3. in un altro terminale, nella cartella della DAW
python serve.py --ace http://localhost:8001
```

Nella DAW apri la scheda **AI · ACE-Step**, lascia l'indirizzo su `/ace`, scrivi la
descrizione e premi **Genera con ACE-Step**. BPM e tonalità vengono presi dal progetto.

Il flusso usato dalla DAW è quello documentato dall'API di ACE-Step:

1. `POST /release_task` con `prompt`, `lyrics`, `audio_duration`, `bpm`, `key_scale` → restituisce `task_id`
2. `POST /query_result` con `task_id_list` finché `status` diventa `1` (riuscito) o `2` (fallito)
3. `GET /v1/audio?path=…` per scaricare il file indicato nel campo `file`

Se sul server è attiva una chiave (`ACESTEP_API_KEY`), inseriscila nel campo **Chiave API**.

`serve.py` fa da ponte: serve la pagina e inoltra `/ace/*` ad ACE-Step, così il browser
non incontra blocchi CORS. ACE-Step può anche girare su un altro computer della rete
(`--ace http://192.168.x.x:8001`).

## Struttura

```
mbstudio91-daw/
├── index.html   # l'intera DAW: interfaccia, motore audio Web Audio, generatore, client ACE-Step
├── serve.py     # server locale + proxy verso ACE-Step (solo libreria standard)
├── LICENSE      # MIT
└── README.md
```

## Roadmap

- [ ] Separazione stem con **Demucs** (`htdemucs`, 4 o 6 stem) come endpoint in `serve.py`
- [ ] Audio → MIDI con **Basic Pitch** (`@spotify/basic-pitch`, gira nel browser)
- [ ] Piano roll e tracce MIDI con strumenti
- [ ] Plugin **Web Audio Modules 2.0** sulle tracce
- [ ] Salvataggio e riapertura progetti (ZIP con audio + JSON)
- [ ] Ridimensionamento e taglio delle clip, automazioni
- [ ] Generazione con **Stable Audio Open** per one-shot e FX (solo uso consentito dalla sua licenza)

## Licenze delle componenti

| Componente | Uso | Licenza |
|---|---|---|
| Questa DAW | tutto il codice in questo repository | MIT |
| ACE-Step 1.5 | servizio esterno, non incluso | dichiarata MIT sulla scheda del modello; verifica il file LICENSE del repository ufficiale |
| Demucs (roadmap) | servizio esterno | verifica il file LICENSE del repository |
| Basic Pitch (roadmap) | libreria | Apache-2.0 |
| Stable Audio Open (roadmap) | modello | Stability AI Community License, uso commerciale solo con licenza Stability |

Il codice di openDAW e GridSound (AGPL-3.0) **non** è incluso: sono stati studiati solo come riferimento,
così questa DAW può restare MIT.

## Note sul prototipo

- I loop generati sono sincronizzati al BPM del momento in cui li crei: se cambi tempo, le clip si
  spostano sulle battute ma l'audio mantiene il tempo originale. Rigenera il loop per adattarlo.
- Gli effetti del generatore (riverbero, delay) sono semplici e servono per bozze e idee.
- Testata su Chrome, Edge e Firefox recenti. Safari funziona, con qualche limite su `StereoPanner` nelle versioni vecchie.
