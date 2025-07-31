#!/bin/bash

echo ""
echo "🔧 Installazione di ESPHomeGUIeasy su macOS"
echo "------------------------------------------"
echo ""

# 🧠 Mostra subito la guida utente
open -a TextEdit ./docs/how_to_install.md 2>/dev/null

# 📁 Copia dell'applicazione in ~/Applications
APP_DIR="$HOME/Applications/ESPHomeGUIeasy"
mkdir -p "$APP_DIR"
echo "📦 Copio i file in: $APP_DIR"
cp -R ./* "$APP_DIR"

cd "$APP_DIR" || {
  echo "❌ Errore: impossibile accedere alla cartella applicazione."
  exit 1
}

# 📂 Creazione struttura operativa in ~/Documents
DOCS_DIR="$HOME/Documents/ESPHomeGUIeasy"
echo "📁 Creo struttura cartelle in: $DOCS_DIR"
mkdir -p "$DOCS_DIR/build"
mkdir -p "$DOCS_DIR/community_projects"
mkdir -p "$DOCS_DIR/user_projects/"{Home_Monitoring,Energy_Power,Security_Alarm,Actuators_IO,Communication,Automation_Logic,Other_Misc}

# 📄 Crea log.txt
touch "$DOCS_DIR/log.txt"

# 📄 Copia user_config.db se non esiste già
if [ ! -f "$DOCS_DIR/user_config.db" ]; then
    cp ./user_config.db "$DOCS_DIR/user_config.db"
    echo "📄 Copiato user_config.db nella cartella Documenti"
else
    echo "ℹ️ user_config.db esiste già. Nessuna azione."
fi

# 🔐 Imposta permessi esecuzione
echo "🔐 Imposto i permessi..."
chmod +x ./esphomeguieasy.command 2>/dev/null
chmod -R +x ./python 2>/dev/null
chmod -R u+rw "$DOCS_DIR" 2>/dev/null

# 🖥️ Crea un alias sul Desktop
DESKTOP_ALIAS="$HOME/Desktop/ESPHomeGUIeasy.command"
if [ ! -f "$DESKTOP_ALIAS" ]; then
    ln -s "$APP_DIR/esphomeguieasy.command" "$DESKTOP_ALIAS"
    echo "🖥️ Collegamento creato sul Desktop: $DESKTOP_ALIAS"
else
    echo "ℹ️ Il collegamento sul Desktop esiste già. Nessuna azione."
fi

# ✅ Conferma completamento
echo ""
echo "✅ Installazione completata con successo!"
echo ""

# 🚀 Avvia l'applicazione
echo "🚀 Avvio dell'applicazione..."
sleep 1

./esphomeguieasy.command || {
  echo ""
  echo "❌ Errore durante l’avvio. Puoi anche avviarla manualmente da:"
  echo "$APP_DIR/esphomeguieasy.command"
  exit 1
}
