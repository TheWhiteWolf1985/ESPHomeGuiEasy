# ✨ Procedura di Rilascio ESPHomeGUIeasy

Questo documento descrive il flusso ufficiale per rilasciare una nuova versione del software nella branch `main`.

---

## 🧱 Branch Strategy

| Branch   | Scopo                                |
|----------|---------------------------------------|
| `develop` | Sviluppo continuo, sperimentazione, tool |
| `main`    | Solo versioni stabili pronte al rilascio |

---

## 🔁 Fasi del Rilascio

### 1. Finalizza lo sviluppo su `develop`
Assicurati che la funzionalità da rilasciare sia completata, testata e funzionante.

### 2. Passa alla branch `main`
```bash
git checkout main
```

### 3. (Facoltativo) Salva un backup
```bash
git branch backup-main
```

### 4. Allinea `main` a `develop`
```bash
git reset --hard develop
```

### 5. Rimuovi i file non destinati alla release
```bash
git rm -r installer_utility/ venv/ .vscode/
git rm *.py *.iss *.bat *.zip *.log
```

### 6. Aggiungi solo i file necessari
```bash
git add main.py gui/ core/ assets/ config/ language/ license/
git add esphomeguieasy.exe start_gui.bat
```

### 7. Commit pulito della release
```bash
git commit -m "🔖 Rilascio ufficiale vX.Y.Z"
```

### 8. Tag della versione
```bash
git tag vX.Y.Z
```

### 9. Push su GitHub
```bash
git push origin main --force
git push origin vX.Y.Z
```

---

## ✅ Note Finali

- `develop` continua ad evolversi liberamente
- `main` viene aggiornata solo in occasione di nuove release
- Se una cartella vuota deve rimanere nel repo, usa un file `.gitkeep`
