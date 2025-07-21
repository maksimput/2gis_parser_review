# REVIEW PARSER 2GIS
***
### Автоматизированный парсер отзывов из 2GIS
***
### ⚙️ Работа
Скрипт парсит отзывы с предприятий 2GIS и сохраняет в CSV-файл в формате таблицы. 
Таблица создается автоматически в корневой директории проекта (reviews.csv). 
Для избежания повторов скрипт сохраняет id всех спаршенных отзывов в отдельный .txt файл. При обнаружения совпадения id происходит автоматическая остановка скрипта.
### ⚙️ Установка 
1. Склонируйте репозиторий (необходим GIT)
``` bash
git clone https://github.com/maksimput/2gis_parser_review.git
```
2. Перейдите в директорию с проектом и соберите образ (необходим Docker)
``` bash
cd 2gis_parser_review
sudo docker build -t 2gis_parser_review .
```
### 🚀 Запуск
``` bash
docker run --rm \
  -e BRANCH_URLS="Ссылки на заведения, откуда нужно собрать отзывы (пример формата - https://2gis.ru/ufa/firm/2393065583018885,https://2gis.ru/ufa/firm/2393066583092767,https://2gis.ru/ufa/firm/2393066583119255).
   Ссылки должны быть без /  в конце. Если ссылок несколько, указываем через запятую" \
  -e TG_BOT_TOKEN="Токен TG-бота" \
  -e TG_CHAT_ID="CHAT_ID TG канала, куда бот отправляет сообщения" \
  -e API_KEY="API ключ 2GIS" \
  -v "$PWD:/app" \
  2gis_parser_review
```

### ❓ Где взять API-ключ 2GIS? 
1. Открываем отзывы любого заведения 2GIS (например https://2gis.ru/ufa/inside/2393172957240294/firm/2393066583092767/55.995445%2C54.697511/tab/reviews?m=55.995521%2C54.697518%2F18)
2. Нажимаем F12, очищаем историю запросов, обновляем страницу
3. Ищем запрос с заголовком reviews?limit=...... (если не находим такой запрос, то листаем страницу пониже примерно на 50 отзывов)
4. В запросе ищем key = ... 
Пример :
public-api.reviews.2gis.com/2.0/branches/2393066583092767/reviews?limit=50&offset=50&is_advertiser=false&fields=meta.providers,meta.branch_rating,meta.branch_reviews_count,meta.total_count,reviews.hiding_reason,reviews.is_verified,reviews.emojis&without_my_first_review=false&rated=true&sort_by=friends&
**key=6e7e1929-4ea9-4a5d-8c05-d601860389bd**&locale=ru_RU
### ⚙️ Автоматизированный запуск раз в сутки через CRON
1. В скрипте run_2gis_parser.sh изменить переменные в соответствии со своими данными.
2. Открыть планировщик CRON
``` bash 
crontab -e 
```
Вписать в файл следующую строку: 
``` bash 
0 18 * * * '/home/administrator/Рабочий стол/review/2gis_parser_review/run_2gis_parser.sh' >> /tmp/reviews.log 2>&1
```
Где 
``` bash 
/home/administrator/Рабочий стол/review/2gis_parser_review/run_2gis_parser.sh 
```
путь до скрипта в директории проекта.

Таким образом проверка отзывов будет осуществляться раз в сутки в 18 часов.