<h1 align="center">housing-filter-control-system</h1>

</h2>

<p align="center">

<img src="https://badges.frapsoft.com/os/v1/open-source.svg?v=103" >

<img src="https://camo.githubusercontent.com/89e8b2eeeb9c2652c1dc087a9f72b514d8a50efd787ffced15c6af9c2c718c14/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f2d507974686f6e2d626c61636b3f7374796c653d666c61742d737175617265266c6f676f3d507974686f6e">

<img src="https://camo.githubusercontent.com/0ced1e0be80f32eee58612df57ae3dbc4aa9fa2e969060fc1491263e6f94d6f3/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f2d4769744875622d3138313731373f7374796c653d666c61742d737175617265266c6f676f3d676974687562">
</p>

# 📖Описание
Данный проект является ботом в Телеграм для поиска квартир по критериям заданными пользователем. Запрос может быть написан в свободной разговорной форме, так как обработкой сообщений занимается NLP модель.  

# 🛠 Технические детали
API сервера:
```python
http://127.0.0.1:8000/get-housing' - создать задачу и получить id задачи
http://127.0.0.1:8000/task/{task_id}' - получить задачу по id
```
