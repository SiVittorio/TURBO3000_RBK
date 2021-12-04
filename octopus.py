from vosk import Model, KaldiRecognizer, SetLogLevel
import moviepy.editor as mp

import os
from os import path
import datetime
import audioop
import wave
import json
import sys
import tkinter as tk
from tkinter import *
from tkinter import messagebox
from tkinter import filedialog as fd

SetLogLevel(0)

# Загрузка списка стоп-слов
with open("stopwords.json") as f:
    stopWords = json.load(f)

# Гланый класс приложения
class Window(Frame):

    def __init__(self, master=None):
        Frame.__init__(self, master)        
        self.master = master
        self.audioPath = None
        self.audioExt = None
        
        # Меню
        menu = Menu(self.master)
        self.master.config(menu=menu)
        fileMenu = Menu(menu)
        fileMenu.add_command(label="Select Media File(s)", command=self.openMedia)
        fileMenu.add_command(label="Select Model Path", command=self.openModelPath)        
        fileMenu.add_command(label="Exit", command=self.exitProgram)
        menu.add_cascade(label="File", menu=fileMenu)

        # Выбор медиа, создание основных компонентов графического интерфейса
        self.frame1 = Frame(self)
        self.frame1.pack(fill=X)

        self.lbl3 = Label(self.frame1, text="Media")
        self.lbl3.pack(side=LEFT, padx=5, pady=5)

        self.scroll_v1 = Scrollbar(self.frame1)
        self.scroll_v1.pack(side=RIGHT, fill="y")

        self.scroll_h1 = Scrollbar(self.frame1, orient=HORIZONTAL)
        self.scroll_h1.pack(side=BOTTOM, fill="x")
        
        self.selectedFiles = Listbox(self.frame1,
                                     xscrollcommand = self.scroll_h1.set,
                                     yscrollcommand = self.scroll_v1.set)
        self.selectedFiles.pack(fill=X, padx=5, pady=5, expand=True)

        self.scroll_h1.config(command=self.selectedFiles.xview)
        self.scroll_v1.config(command=self.selectedFiles.yview)

        # Выбор модели
        self.frame2 = Frame(self)
        self.frame2.pack(fill=X)

        self.lbl4 = Label(self.frame2, text="Model")
        self.lbl4.pack(side=LEFT, padx=5, pady=5)

        self.modelPath = Label(self.frame2)
        self.modelPath.pack(fill=X, expand=1)
        
        # Кнопки
        self.frame3 = Frame(self)
        self.frame3.pack(fill=X)
        
        self.btnConvertText = Button(self, text='Convert To Text', command=self.convertText)
        self.btnConvertText.pack(fill=X)

        # Логгирование событий
        self.frmTxt = Frame(self)
        self.frmTxt.pack(fill=BOTH, expand=1)
        
        self.vsb = Scrollbar(self.frmTxt, orient='vertical')
        self.vsb.pack(side=RIGHT, fill=Y)        
        self.txtLog = Text(self.frmTxt, yscrollcommand=self.vsb.set)
        self.txtLog.pack(fill=BOTH, expand=1)
        self.vsb.config(command=self.txtLog.yview)

        self.pack(fill=BOTH, expand=1)

        # Используется для ускорения
        self.prevModelName = ""
    
    # Выйти из приложения
    def exitProgram(self):
        exit()

    # Загрузить языковую модель
    def openModelPath(self):
        name = fd.askdirectory()
        self.modelPath.config(text=name)

    # Згагрузить медиа объекты (видео .mp4 и аудио .wav) 
    def openMedia(self):
        names = fd.askopenfilenames(filetypes=[("Media files", "*.mp4 *.wav")])
        if names: 
            self.audioPaths, self.audioExts = zip(*list(map(os.path.splitext, names)))
            for n in names:
                self.selectedFiles.insert(END, n)
        else:
            self.audioPaths = None

    # Логгирование сообщений
    def logMsg(self, msg):
        ct = datetime.datetime.now()
        self.txtLog.insert(END, str(ct) + ": " + msg + "\n")
        self.txtLog.see(END)
        Tk.update_idletasks(self)


    # Удаление логов из журнала 
    def clearLog(self):
        self.txtLog.delete(0.0, END)
        
    # Конвертирование аудио в текст
    def convertText(self):
        # Проверка, помнялась ли языковая модель и нужно ли загружать новую
        if self.modelPath.cget("text") and self.prevModelName != self.modelPath.cget("text"):
            self.logMsg("LOADING LANGUAGE MODEL...")
            self.prevModelName = self.modelPath.cget("text")
            self.model = Model(self.prevModelName)
        self.logMsg("Start Text Conversion")
        self.logMsg("******************************************************")
        self.processAllMedia()
        self.logMsg("Text Conversion Processing Complete\n")
        self.logMsg("******************************************************")

    # Преобразовать все медиа материалы в текст
    def processAllMedia(self):
        for i in range(self.selectedFiles.size()):
            name = self.selectedFiles.get(i)
            
            # Проверка, является ли данный медиа файл видео
            if name[-4:].lower() == ".mp4":
                #Преобразование из .mp4 в .wav
                audioPath, _ = os.path.splitext(name)
                clip = mp.VideoFileClip(name)
                name = f"{audioPath}.wav"
                clip.audio.write_audiofile(name)
            
            r = self.processFile(name)
            if not r: break

    # Обработка одного аудио файла 
    def processFile(self, audioName):
        if self.modelPath.cget("text") == "":
            messagebox.showinfo("AudioText", "No model file is selected. Please, select a model path.")
            return False

        audioPath, audioExt = os.path.splitext(audioName)
            
        self.logMsg("convert stereo wav to mono wav")
        
        try:
            # Открываем два wave файла: первый - данное или сгенерированное аудио, второй - аналогичное аудио, 
            # только в моно формате
            inFile = wave.open(audioName,'rb')
            self.monoWav = audioPath + "_Mono" + audioExt
            outFile = wave.open(self.monoWav,'wb')
            outFile.setnchannels(1)
            outFile.setsampwidth(inFile.getsampwidth())
            outFile.setframerate(inFile.getframerate())
            soundBytes = inFile.readframes(inFile.getnframes())
            monoSoundBytes = audioop.tomono(soundBytes, inFile.getsampwidth(), 1, 1)
            outFile.writeframes(monoSoundBytes)
            self.logMsg("Finished exporting Mono WAV file:{}".format(self.monoWav))
        except Exception as e:
            messagebox.showinfo("Error Converting WAV stereo To WAV Mono", e)
            return False
        finally:
            inFile.close()
            outFile.close()
        
        try:
            # Конвертирование видео в .json, содержащий распознанные слова и их "важностЬ" в тексте, а 
            # .txt файл,содержащищй весь распознаный текс.
            self.logMsg("convert mono wav to json text")
            inFileName = self.monoWav
            splitFile = os.path.splitext(inFileName)
            self.jsonPath = splitFile[0]
            # Слова в тексте, записанные в .json
            outfileResults = self.jsonPath + "-Results.json"
                        
            self.logMsg("Open WAV file.")
            wf = wave.open(inFileName, "rb")

            results = []
            textResults = []

            # Главный цикл обработки информации, считанной из файла
            self.logMsg("Start recognizer.")
            # Иниципализация распознавателя
            self.recognizer = KaldiRecognizer(self.model, wf.getframerate())
            self.recognizer.SetWords(True)
            self.logMsg("Process audio file.")
            while True:
                # Считать данные из .wav файла размером 4000 байт
                data = wf.readframes(4000)
                # Если данных нет, прекратить обработку
                if len(data) == 0:
                    break
                elif self.recognizer.AcceptWaveform(data):
                    recognizerResult = self.recognizer.Result()
                    # Обработка "сырого" .json
                    resultDict = json.loads(recognizerResult)
                    if "result" in resultDict:
                        for rec in resultDict["result"]:
                            if rec["word"] not in stopWords:
                                results.append(rec)
                    if "text" in resultDict:
                        textResults.append(resultDict["text"])
            
`           # Обработка последних значений для распознавателя
            resultDict = json.loads(self.recognizer.FinalResult())
            if "result" in resultDict:
                for rec in resultDict["result"]:
                    if rec["word"] not in stopWords:
                        results.append(rec)
            if "text" in resultDict:
                textResults.append(resultDict["text"])

            # Подсчёт "важности" каждого слова в тексте
            from collections import Counter
            cnt = Counter(map(lambda r: r["word"], results))
            for rec in results:
                rec["weight"] = cnt[rec["word"]]
            
            for rec in results:
                rec["weight"] = cnt[rec["word"]]

            with open(outfileResults, 'w') as output:
                print(json.dumps(results, indent=4, ensure_ascii=False), file=output)
                self.logMsg("Finished exporting json results file:{}".format(outfileResults))

            with open(outfileText, 'w') as output:
                #data = { "text": "".join(textResults) }
                #print(json.dumps(data, indent=4,ensure_ascii=False), file=output)

                f = open(f"{audioPath}.txt", "w")
                f.write(" ".join(textResults))                

                self.logMsg("Finished exporting json text file:{}".format(outfileText))
            
        except Exception as e:
            messagebox.showinfo("Error Converting mono WAV stereo to json text file", e)
            return False

        return True

        
root = Tk()
app = Window(root)
root.wm_title("OCTOPUS")
root.geometry("600x600")
root.mainloop()
