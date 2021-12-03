OCTOPUS
-----------------------------------
Программа OCTOPUS позволят из видео(которое должно быть со звуком) получить 2 json файла : 
  1. Текстовую запись всей речи из видеофайла
  2. Ключевые слова из этой записи

## Установка
Обязательно наличие среды python на компьютере. Скачать его можно на официальном сайте: https://www.python.org/downloads/

После установки python требуется инсталлировать три библиотеки.
В терминале(командной строке) пишем:

```
pip install vosk
pip install pydub
pip install ffmpeg
pip install yola
pip install gensim
pip install pymorphy2
pip install scipy
pip install counter

```
Для работы gensim необходимо использовать бинарный модуль, который можно скачать с сайта https://rusvectores.org/ru/models/, подойдет любой, но чем больше вес, тем больше точность и кол-во известных системе слов
