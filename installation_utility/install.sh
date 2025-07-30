#!/bin/bash
# Script di installazione per ESPHomeGUIeasy (Linux)

# Directory documenti e config utente (puoi adattare se vuoi una struttura diversa)
USER_DOCS="$HOME/ESPHomeGUIeasy"
CONFIG_DIR="$HOME/.config/ESPHomeGUIeasy"

echo "Creazione directory di lavoro nella home utente..."

mkdir -p "$USER_DOCS/build"
mkdir -p "$USER_DOCS/user_projects"
mkdir -p "$USER_DOCS/community_projects"

mkdir -p "$USER_DOCS/user_projects/Home_Monitoring"
mkdir -p "$USER_DOCS/user_projects/Energy_Power"
mkdir -p "$USER_DOCS/user_projects/Security_Alarm"
mkdir -p "$USER_DOCS/user_projects/Actuators_IO"
mkdir -p "$USER_DOCS/user_projects/Communication"
mkdir -p "$USER_DOCS/user_projects/Automation_Logic"
mkdir -p "$USER_DOCS/user_projects/Other_Misc"

echo "✅ Cartelle principali create."

# Copia user_config.db solo se presente nel pacchetto
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

echo ""
echo "Installazione completata!"
echo "Puoi ora avviare ESPHomeGUIeasy con ./esphomeguieasy.sh"
