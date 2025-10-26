#!/bin/bash
set -e

if [ "$#" -ne 4 ]; then
    echo "Usage: $0 CLIENT_NAME CLIENT_PUBLIC_KEY WG_CONFIG_FILE DOCKER_CONTAINER"
    exit 1
fi

CLIENT_NAME="$1"
CLIENT_PUBLIC_KEY="$2"  # Для совместимости, но не используется для поиска
WG_CONFIG_FILE="$3"
DOCKER_CONTAINER="$4"

pwd=$(pwd)
mkdir -p "$pwd/files"
SERVER_CONF_PATH="$pwd/files/server.conf"

# 1. Копируем текущий конфиг из контейнера
echo "🔹 Шаг 1: Получаем текущий wg0.conf из контейнера..."
docker exec -i "$DOCKER_CONTAINER" cat "$WG_CONFIG_FILE" > "$SERVER_CONF_PATH"

# 2. Удаляем ВСЕ блоки [Peer], где первый комментарий — # CLIENT_NAME
echo "🔹 Шаг 2: Удаляем все блоки [Peer] с именем '$CLIENT_NAME'..."
awk -v name="$CLIENT_NAME" '
    BEGIN { in_peer=0; skip=0; peer_lines="" }
    /^\[Peer\]/ {
        if (in_peer && !skip) printf "%s", peer_lines
        in_peer=1
        skip=0
        peer_lines=$0 "\n"
        next
    }
    in_peer {
        peer_lines = peer_lines $0 "\n"
        if (/^# /) {
            gsub(/^# /, "", $0)
            gsub(/\[.*\]/, "", $0)
            gsub(/^[ \t]+|[ \t]+$/, "", $0)
            if ($0 == name) {
                skip=1
            }
        }
        if (/^\[Peer\]/ || /^\[Interface\]/ || $0 == "") {
            if (in_peer && !skip) printf "%s", peer_lines
            in_peer=0
            skip=0
            peer_lines=""
            if (/^\[Peer\]/ || /^\[Interface\]/) {
                print
            }
            next
        }
        next
    }
    { print }
    END {
        if (in_peer && !skip) printf "%s", peer_lines
    }
' "$SERVER_CONF_PATH" > "$SERVER_CONF_PATH.tmp"

mv "$SERVER_CONF_PATH.tmp" "$SERVER_CONF_PATH"

# 3. Проверяем, что файл изменился
if diff "$SERVER_CONF_PATH" <(docker exec -i "$DOCKER_CONTAINER" cat "$WG_CONFIG_FILE") >/dev/null; then
    echo "⚠️ Конфигурация не изменилась — возможно, клиент не найден."
else
    echo "✅ Конфигурация успешно изменена."
fi

# 4. Загружаем обновлённый конфиг обратно в контейнер
echo "🔹 Шаг 3: Загружаем обновлённый wg0.conf в контейнер..."
docker cp "$SERVER_CONF_PATH" "$DOCKER_CONTAINER":"$WG_CONFIG_FILE"

# 5. Перезапускаем контейнер — это гарантирует, что WireGuard перечитает конфиг
echo "🔹 Шаг 4: Перезапускаем контейнер '$DOCKER_CONTAINER'..."
docker restart "$DOCKER_CONTAINER"

# Ждём, пока контейнер полностью запустится
sleep 5

# 6. Удаляем локальные файлы клиента
echo "🔹 Шаг 5: Удаляем локальную папку клиента..."
rm -rf "users/$CLIENT_NAME"

# 7. Обновляем clientsTable в контейнере
echo "🔹 Шаг 6: Обновляем clientsTable в контейнере..."
CLIENTS_TABLE_PATH="$pwd/files/clientsTable"
docker exec -i "$DOCKER_CONTAINER" cat /opt/amnezia/awg/clientsTable > "$CLIENTS_TABLE_PATH" 2>/dev/null || echo "[]" > "$CLIENTS_TABLE_PATH"

if [ -f "$CLIENTS_TABLE_PATH" ]; then
    jq --arg name "$CLIENT_NAME" 'map(select(.userData.clientName != $name))' "$CLIENTS_TABLE_PATH" > "$CLIENTS_TABLE_PATH.tmp"
    mv "$CLIENTS_TABLE_PATH.tmp" "$CLIENTS_TABLE_PATH"
    docker cp "$CLIENTS_TABLE_PATH" "$DOCKER_CONTAINER":/opt/amnezia/awg/clientsTable
    echo "✅ clientsTable обновлён."
fi

echo "🎉 Все клиенты с именем '$CLIENT_NAME' успешно удалены из контейнера и локальной системы."