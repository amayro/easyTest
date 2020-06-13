EasyTest
===============


Django 2.1 quiz application. 

Удобное джанго приложение для развертывания системы тестирования, создания групп, студентов и отслеживания результатов.  

Configure your quizzez and assign students to the groups.  
Easy quiz platform is aimed at helping teachers or school administration in deploying groups, creating and assigning quizzez, and checking student results.


![Order type Question](https://i.imgur.com/2r1CsfZ.jpg "Question picture hosted by Imgur")


Current features
----------------

Для пользователя (студента):  
* Вход под ранее созданным экзаменатором (преподавателем) аккаунтом 
* Вывод доступных тестов с принадлежностью к группе 
* Прохождение теста 
* Отложить вопрос при прохождении теста (ответить позже) 
* Вывод неправильных ответов и прочей информации в конце теста 
* Просмотр результатов ранее пройденных тестов 

Для персонала (преподавателя): 
* Создание аккаунтов для студентов 
* Создание групп и назначение тестов определенным группам 
* Разделение студентов по группам 
* Создание и изменение тестов двумя способами – заполняя поля ввода данными либо загрузкой через json 
* Скачивание ранее созданного теста в формате json 
* Назначение одного вопроса для нескольких тестов 
* Несколько типов вопросов - Drag and Drop (порядок), мультивыбор (один и несколько правильных ответов) 
* Ограничение количества вопросов в тесте 
* Ограничение по времени на прохожождение теста 
* Просмотр результатов студентов 
* В дополнении к django-admin реализована собственная админка адаптированная с сайтом (операции CRUD для тестов, профилей студентов, групп, встроенные в дизайн сайта) 

Прочее: 
* Регистрация только для экзаменатора 
* Рандомный вывод вопросов в тесте 
* Проверки на валидность форм и прав на доступ к функционалу 
* Запуск проекта через Dockerfile 
* Интернационализация сайта (django-rosetta) 
* Удаление тестов без удаления из базы (soft delete)



![Result page](https://i.imgur.com/9PZ0nSY.jpg "Result picture hosted by Imgur")

Requirements
------------
python 3.6 or above  

Django==2.1.2  
pytz==2018.5  
commentjson==0.7.1  

Installation
------------

```sh
$  pip install -r requirements.txt
```

```sh
$ python manage.py runserver

```


Collaborators
------------

* [https://github.com/amayro](https://github.com/amayro)
* [https://github.com/ESm1th](https://github.com/ESm1th)
* [https://github.com/timrestDm](https://github.com/timrestDm)
* [https://github.com/ziphead](https://github.com/ziphead)
