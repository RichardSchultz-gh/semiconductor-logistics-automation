# SE Projekt Frau Holle
# Team I04 - Nils Generlich, Yannik-Joel Herrchen, Nico Kroll, Paul Marx, Richard Schulze, Marlene Winter
# MIT Lizenz 2024 
# backup.sh
#!/bin/bash

# Zielverzeichnis für das Backup
BACKUP_DIR="C:/Users/xxx/i04-projekt-frau-holle-main/src/backup"

# Datenbank-Parameter
DB_NAME="postgres"
DB_USER="postgres"
DB_HOST="localhost"
DB_PORT="5432"

# Dateiname für das Backup mit Datum und Uhrzeit
BACKUP_FILE="$BACKUP_DIR/backup_$(date +'%Y%m%d_%H%M%S').sql"

# Ausführen von pg_dump, um die gesamte Datenbank zu sichern
pg_dump -U $DB_USER -h $DB_HOST -p $DB_PORT $DB_NAME > $BACKUP_FILE

# Überprüfen, ob der Befehl erfolgreich war
if [ $? -eq 0 ]; then
    echo "$(date +'%Y-%m-%d %H:%M:%S') - Backup erfolgreich abgeschlossen." >> "$BACKUP_DIR/backup.log"
else
    echo "$(date +'%Y-%m-%d %H:%M:%S') - Backup fehlgeschlagen." >> "$BACKUP_DIR/backup.log"
fi
