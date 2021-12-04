OCTOPUS
-----------------------------------
Программа OCTOPUS позволят из видео(которое должно быть со звуком) получить 2 json файла и один текстовый : 
  1. Текстовую запись всей речи из видеофайла
  2. Ключевые слова из этой записи
  3. Субтитры

## Установка
Обязательно наличие среды python на компьютере. Скачать его можно на официальном сайте: https://www.python.org/downloads/

После установки python требуется инсталлировать несколько библиотек.
В терминале(командной строке) пишем:

```
pip install vosk
pip install pydub
pip install ffmpeg
pip install yola
pip install gensim
pip install pymorphy2
pip install pymorphy2-dicts
pip install DAWG-Python
pip install scipy
pip install counter
```
Для работы gensim необходимо использовать бинарную модель, которую можно скачать с сайта https://rusvectores.org/ru/models/, мы использовали модель "news_upos_skipgram_300_5_2019", но подойдут и другие с расширением .bin и тагсетом "Universal tags ". Чем больше вес, тем больше точность и кол-во известных системе слов. 

Также для возможности исполнения octopus.py нужно скачать файл "stopwords.json" из нашего репозитория и переместить его в папку с файлом "octopus.py"

## Использование
Необходимо открыть терминал, перейти в директорию с файлом "octopus.py", далее

Для windows:
```
python octopus.py
```
Для linux:
```
python3 octopus.py
```
В верхней строке меню кликаем на File -> Select Media File(s), где выбираем 1 или несколько видеофайлов, затем File -> Select Model Path, где выбираем папку библиотеки(например vosk-model-small-ru-0.22) и жмём на кнопку Convert To Text

На выходе программы получаем 3 файла

1. video_name.txt - субтитры к тексту без какой-либо разметки
2. video_name_Mono-Results.json - записывается каждое считанное слово, а к нему параметры "start"(начало произнесения слова в секундах), "end"(конец произнесения слова в секундах) и weight(вес выражения как ключевого слова)
3. video_name_Mono-Text.json - текст к видео в формате json

## Использование text_detector.py 
