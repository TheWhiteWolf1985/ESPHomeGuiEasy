#!/bin/bash
# Script di installazione per ESPHomeGUIeasy (Linux)

# 🧠 Mostra subito la guida utente appena parte lo script
if [ -f "./docs/how_to_install.md" ]; then
    xdg-open ./docs/how_to_install.md >/dev/null 2>&1 &
fi

# Directory documenti e config utente (fissa: ~/Documents/ESPHomeGUIeasy)
USER_DOCS="$HOME/Documents/ESPHomeGUIeasy"
CONFIG_DIR="$HOME/.config/ESPHomeGUIeasy"

echo "📁 Creazione directory di lavoro in: $USER_DOCS"

mkdir -p "$USER_DOCS/build"
mkdir -p "$USER_DOCS/user_projects"
mkdir -p "$USER_DOCS/community_projects"

for folder in Home_Monitoring Energy_Power Security_Alarm Actuators_IO Communication Automation_Logic Other_Misc; do
    mkdir -p "$USER_DOCS/user_projects/$folder"
done

echo "✅ Cartelle principali create."

# Copia user_config.db solo se presente
if [ -f "./user_config.db" ]; then
    mkdir -p "$CONFIG_DIR"
    cp -n "./user_config.db" "$CONFIG_DIR/user_config.db"
    echo "✅ Copiato user_config.db in $CONFIG_DIR"
else
    echo "⚠️  user_config.db non trovato nella cartella corrente."
fi

# Copia licenza, se presente
if [ -d "./License" ]; then
    cp -r "./License" "$USER_DOCS/"
    echo "✅ Cartella License copiata in $USER_DOCS/"
fi

# 🔒 Imposta permessi di esecuzione sui file chiave
chmod +x ./install.sh
chmod +x ./esphomeguieasy.sh
chmod +x ./python/bin/python3


echo ""
echo "🚀 Installazione completata!"
echo "Puoi ora avviare ESPHomeGUIeasy con: ./esphomeguieasy.sh"
