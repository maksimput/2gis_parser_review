cd '/home/administrator/Рабочий стол/review/2gis_parser_review' #Абсолютный путь до директории с проектом
docker run --rm \
  -e BRANCH_URLS="https://2gis.ru/ufa/firm/2393065583018885,https://2gis.ru/ufa/firm/2393066583092767,https://2gis.ru/ufa/firm/2393066583119255).
   Ссылки должны быть без /  в конце. Если ссылок несколько, указываем через запятую" \
  -e TG_BOT_TOKEN="Токен TG-бота" \
  -e TG_CHAT_ID="CHAT_ID TG канала, куда бот отправляет сообщения" \
  -e API_KEY="API ключ 2GIS" \
  -v "$PWD:/app" \
  2gis_parser_review
