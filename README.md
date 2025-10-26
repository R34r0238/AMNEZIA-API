# AMNEZIA-API(Ubuntu 22.04+)



Модуль удаленного управления AmneziaVPN(добавление, удаление пользователей) Развертка на сервер



Как использовать:


Предустановить через официальное приложение AmneziaVPN сервер с протоколом AmneziaWG, иметь на сервере предустановленный Python3.11 и выше (apt-get install python3.11)


1 - Создайте на сервере папку amnezia-api, скопируйте в нее файлы с репозитория


2 - cd amnezia-api

3 - apt install python3.11-venv

4 - apt install -y jq

5 - chmod +x install-api.sh
   ./install-api.sh
	
6 - python3.11 -c 'import db; db.create_config()'(введите рандом ID, random токен, это нужно для инициализация так как модуль вырезан из чужого проекта)

7 - AMNEZIA_API_SECRET=secret-key AMNEZIA_API_HOST=IP AMNEZIA_API_PORT=8081 python3.11 api.py & (secret-key придумываете любой надежный, IP - вводите ip сервера на котором устанавливаете модуль)

8 - Готово (работают функции add_user, delete_user, get_key_info, пример использования есть в файле exemple.py)

