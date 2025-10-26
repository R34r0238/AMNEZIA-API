#!/bin/bash
set -e

GREEN=$'\033[0;32m'
RED=$'\033[0;31m'
NC=$'\033[0m'

echo -e "${GREEN}Установка Amnezia API...${NC}"

# Требуется Python 3.11
if ! command -v python3.11 &>/dev/null; then
    echo -e "${RED}Требуется Python 3.11${NC}"
    exit 1
fi

# Создаём venv
python3.11 -m venv myenv
source myenv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Права на скрипты
chmod +x newclient.sh removeclient.sh

# Проверяем наличие AmneziaWG
if ! docker ps --format '{{.Names}}' | grep -q "amnezia-awg"; then
    echo -e "${RED}Контейнер amnezia-awg не запущен! Установите AmneziaVPN.${NC}"
    exit 1
fi

# Инициализация (если нет setting.ini)
if [ ! -f "files/setting.ini" ]; then
    echo -e "${GREEN}Выполните инициализацию: python3.11 -c 'import db; db.create_config()'${NC}"
fi

echo -e "${GREEN}Установка завершена.${NC}"
echo "Запуск: source myenv/bin/activate && AMNEZIA_API_SECRET=ваш_секретный_ключ python3.11 api.py"