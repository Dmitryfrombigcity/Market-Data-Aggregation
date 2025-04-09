## Расчёт стоимости портфеля при реализации простой инвестиционной стратегии
![pic1](https://github.com/user-attachments/assets/43dcd15b-e525-4ad9-824f-7e0488151656)

## Основная идея
Ежемесячная покупка акций на фиксированную сумму, а также вложение дивидендов в покупку акций.

## Основные условия
- Покупка акций совершается в определённый день месяца.
- Покупка на дивиденды совершается через определённый промежуток времени после их объявления.

## Настройки
Изначальные условия задаются в файле `.env`. Большинство из них имеют значения по умолчанию и валидируются с помощью [Pydantic](https://docs.pydantic.dev/).  
Реально необходимыми являются только настройки базы данных.

### Пример файла `.env`
```
DB_HOST=localhost
POSTGRES_PORT=5432
DB_USER=user
DB_PASS=password
DB_NAME=aggregation

POOL_MAX_SIZE=15                     # Максимальный размер пула соединений PostgreSQL (по умолчанию 50)
TCPConnectorLimit=100                # Максимальный размер пула соединений aiohttp (по умолчанию 100)
SERVER_PORT=8050                     # Номер порта сервера Flask (по умолчанию 8050)

MONTHLY_INVESTMENTS=2000             # Ежемесячный платёж (по умолчанию 1000, больше 0)
DIVIDENDS_PURCHASE_DAY_OFFSET=2      # Промежуток, через который покупаются акции на дивиденты
                                     # (по умолчанию 8, от 0 до 28)
MONTHLY_PURCHASE_DAY=1               # День месяца, в который регулярно покупаются акции
                                     # (по умолчанию 1, от 1 до 28)
LIMIT_OF_DAYS_FOR_PRICE_SEARCH=28    # Максимальное количество дней без торгов по акции, при превышении считается,
                                     # что акции сняты с торгов (по умолчанию 28, от 1 до 28)

BUNCH_OF_TICKERS=SBER,LKOH           # Набор акций (по умолчанию SBER, LKOH)
```

## Запуск проекта

Проект использует [PostgreSQL](https://www.postgresql.org/) на Docker, если у вас не установлен Docker, [установите его](https://www.docker.com/).

Далее программа ищет PostgreSQL согласно переменным окружения. Можно также использовать локальную базу данных.

Происходит сбор информации с биржи [MOEX](https://www.moex.com/) с помощью [AIOHTTP](https://docs.aiohttp.org/en/stable/).

## Обработка данных

Создаются две таблицы:

- **results_of_trades** — с результатами регулярных торгов.
- **dividends** — с выплатами дивидендов.

Таблицы создаются при первом запуске, а при последующих проверяется наличие новых данных и их обновление.  
При любой ошибке во время сетевых операций таблица очищается, чтобы при следующем запуске создать её заново, 
так как это может привести к нарушению целостности данных.  
Альтернативный вариант-- вести журнал сессий и откатываться только до предыдущей ( не реализовано).

В таблице `results_of_trades` заполняются все отсутствующие даты (выходные дни, в которые торги не ведутся).  
Это необходимо для того, чтобы если дата покупки акций попадает на выходной,  
мы могли рассмотреть следующий рабочий день в пределах `LIMIT_OF_DAYS_FOR_PRICE_SEARCH`.

Далее данные из таблиц `results_of_trades` и `dividends` агрегируются согласно заданным условиям и передаются в программу для расчёта.

Во время обработки заполняется таблица **processed_data** со следующими полями:

- **id** — номер записи.
- **date** — дата.
- **ticker** — акция.
- **expenses** — сумма расходов на данную дату.
- **shares** — количество акций на данную дату.
- **capitalization** — капитализация на данную дату.
- **price** — биржевая цена акции на данную дату.
- **monthly_balance** — остаток средств на данную дату.

Если после покупки акций остаются средства, они переносятся на следующую покупку.  
Таблица `processed_data` заполняется заново при каждом запуске, так как она создаётся под конкретные условия.

## Визуализация данных

Отображение данных производится в окне браузера с помощью [Plotly Dash](https://dash.plotly.com/). Интерфейс интуитивно понятен.

Торги разными акциями могли начаться в разное время, поэтому значения в колонке `expenses` для разных акций могут отличаться.  
Исходя из этого, чекбокс **"Select expenses"** доступен только при выборе одного графика.

Визуализацию можно запустить отдельной командой, и она будет использовать данные, сохранённые в базе.
![pic2](https://github.com/user-attachments/assets/23aad819-f3fa-4ed3-ad5d-eecf26c6fec9)

## Логирование
Вывод большинства ошибок подавляется, и выводится лишь сообщение о том, что произошла ошибка.  
При этом подробный отчёт записывается в `logs/logging.txt` с помощью [Loguru](https://loguru.readthedocs.io/en/stable/).  

------------
[![ubuntu-latest  windows-latest macos-latest](https://github.com/Dmitryfrombigcity/Market-Data-Aggregation/actions/workflows/os_test.yml/badge.svg)](https://github.com/Dmitryfrombigcity/Market-Data-Aggregation/actions/workflows/os_test.yml)
## Клонирование проекта и установка зависимостей
Для начала работы с проектом необходимо склонировать репозиторий на ваш компьютер.  
Для этого выполните следующую команду в терминале:
```
git clone https://github.com/Dmitryfrombigcity/Market-Data-Aggregation
```
### Перейдите в директорию проекта:
```
cd Market-Data-Aggregation
```
В системе должен быть один из поддерживаемых интерпретаторов, если нет, то [установите](https://www.python.org/downloads/)   
[![python-3.12](https://github.com/Dmitryfrombigcity/Market-Data-Aggregation/actions/workflows/python-3.12.yml/badge.svg)](https://github.com/Dmitryfrombigcity/Market-Data-Aggregation/actions/workflows/python-3.12.yml)
[![python-3.13](https://github.com/Dmitryfrombigcity/Market-Data-Aggregation/actions/workflows/python-3.13.yml/badge.svg)](https://github.com/Dmitryfrombigcity/Market-Data-Aggregation/actions/workflows/python-3.13.yml)  

## Установка зависимостей
Если вы используете `pip`:  
### Создайте и активируйте виртуальное окружение:  
*Возможно придётся указать путь к интерпретатору.*
```
pip install virtualenv
virtualenv -p python3.12 venv
source venv/bin/activate
```
*Для Windows активация будет другая:*
```
venv\Scripts\activate.bat
```
### Установите зависимости из файла requirements.txt:
```
pip install -r requirements.txt
```
### Если вы предпочитаете использовать Poetry, выполните следующие шаги:
Убедитесь, что [Poetry](https://python-poetry.org/) установлен. Если нет, установите его:
```
pip install poetry
```
### Установите зависимости проекта:
```
poetry install
```
### Активируйте виртуальное окружение, созданное Poetry:
```
poetry shell
```
### Запустите программу:
```
python main.py
```
### Для запуска только визуализации:
```
python dash_only.py
```
При закрытии вкладки браузера, программа и сервер завершат работу.

## Тестирование
Для тестирования сетевых соединений применяется `Mocking`.  
Для проверки работы с базой данных используется тестовая база с предопределенным набором данных.
### Запуск тестов:
```
cd Market-Data-Aggregation/   
pytest --verbose
```
## Используемые технологии:
- *Python*
- *asyncio*
- *AIOHTTP*
- *Pydantic*
- *pydantic-settings*
- *PostgreSQL*
- *psycopg*
- *psycopg-pool*
- *Pytest*
- *pytest-dotenv*
- *pytest-mock*
- *pytest-asyncio*
- *Docker*
- *Dash*
- *dash-ag-grid*
- *dash-bootstrap-components*
- *Loguru*
## Disclaimer
Программа не учитывает некоторые особенности работы биржи, например **stock split**.  
При странном поведении графика всегда можно проверить данные на вкладке **Grid**.


