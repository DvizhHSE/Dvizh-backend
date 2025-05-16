# Dvizh-backend
## Руководство по запуску (пример)
Работа выполняется в терминале для данного проекта (например, в pycharm)
1) python -m venv venv
2) venv\Scripts\activate
3) pip install -r requirements.txt --force-reinstall
4) uvicorn main:app --reload
## Документация:
1) http://127.0.0.1:8000/redoc
2) http://127.0.0.1:8000/docs
## Возможно будут проблемы с подключением к Mongo, так как там нужно добавлять разрешенные IP-адреса. В таком случае писать @Temik_mus
