import os
from os import path
import datetime
from pydub import AudioSegment
import audioop
import wave
import json
import sys

from vosk import Model, KaldiRecognizer, SetLogLevel

import tkinter as tk
from tkinter import *
from tkinter import messagebox
from tkinter import filedialog as fd 


SetLogLevel(0)

class Window(Frame):

    def __init__(self, master=None):
        Frame.__init__(self, master)        
        self.master = master
        self.audioPath = None
        self.audioExt = None

        # if running the compiled version then tell pydub where the ffmpeg exe is found.
        if getattr(sys, 'frozen', False):
            this_script_dir = path.dirname(path.realpath(__file__))
            os.environ["PATH"] += os.pathsep + this_script_dir + '\\ffmpeg'

        # print(os.environ["PATH"])
        
        # menu system
        menu = Menu(self.master)
        self.master.config(menu=menu)
        fileMenu = Menu(menu)
        fileMenu.add_command(label="Select Model Path", command=self.openModelPath)
        fileMenu.add_command(label="Select Audio File", command=self.loadAndConvertVideos)
        fileMenu.add_command(label="Exit", command=self.exitProgram)
        menu.add_cascade(label="File", menu=fileMenu)

        # model file controls
        self.lbl3 = Label(self, text="Language Model", font= ('Helvetica', 18, 'bold'))
        self.lbl3.place(x=5,y=0)
        self.lbl4 = Label(self, text="Model Path:")
        self.lbl4.place(x=10,y=40)
        self.modelPath = tk.StringVar()
        self.txtBoxPath = Label(self, textvariable = self.modelPath)
        self.txtBoxPath.place(x=90, y = 40)
        
        # input file controls
        self.lbl0 = Label(self, text="Input Audio File", font= ('Helvetica', 18, 'bold'))
        self.lbl0.place(x=5,y=60)
        self.lbl1 = Label(self, text="File Name:")
        self.lbl1.place(x=10,y=100)
        self.audioFileName = tk.StringVar()
        self.txtBoxName = Label(self, textvariable = self.audioFileName)
        self.txtBoxName.place(x=70, y = 100)
        self.lbl2 = Label(self, text="File Type:")
        self.lbl2.place(x=10,y=120)
        self.audioFileType = tk.StringVar()
        self.txtBoxType = Label(self, textvariable = self.audioFileType)
        self.txtBoxType.place(x=70, y = 120)
        
        # buttons
        self.btnConvertText = Button(root, text = 'Convert To Text', bd = '5',  command = self.convertText)
        self.btnConvertText.place(x=10, y=150)
        
        # text area
        self.frmTxt = Frame(root, height = 20, width = 70)
        self.frmTxt.pack(side=LEFT)
        self.frmTxt.place(x=10, y=190)
        
        self.vsb = Scrollbar ( self.frmTxt, orient='vertical' )
        self.vsb.pack( side = RIGHT, fill = Y )        
        self.txtLog = Text(self.frmTxt, height = 20, width = 70, yscrollcommand = self.vsb.set)
        self.txtLog.pack(side=LEFT, fill=Y)
        self.vsb.config( command = self.txtLog.yview )
        
        # widget can take all window
        self.pack(fill=BOTH, expand=1)
        
    def exitProgram(self):
        exit()

    def openModelPath(self):
        'select path to language model'
        name = fd.askdirectory()
        self.modelPath.set(name)
        
    def openAudioFiles(self):
        'open audio files'
        names = fd.askopenfilenames(filetypes=[("Video files", "*.mp4")]) 

        print(type(names))

        self.audioFileName.set(name)
        splitFile = os.path.splitext(name)
        self.audioPath = splitFile[0]
        self.audioExt = splitFile[1]
        self.audioFileType.set(self.audioExt)

    def loadAndConvertVideos(self):
        names = fd.askopenfilenames(filetypes=[("Video files", "*.mp4")]) 
        print(names)

    def logMsg(self, msg):
        ct = datetime.datetime.now()
        self.txtLog.insert(END, str(ct) + ": " + msg + "\n")
        self.txtLog.see(END)
        Tk.update_idletasks(self)

    def clearLog(self):
        self.txtLog.delete(0.0, END)
        
    def convertText(self):
        self.logMsg("Start Text Conversion")
        self.clearLog()
        self.processFiles()
        self.logMsg("Text Conversion Processing Complete")
            
    def processFiles(self):
        '''
        this method converts the audio file to text.  This is a three step process:
        1. convert mp3 file to wav file - this step is skipped if you start with a WAV file
        2. convert wav file to mono file
        3. process the mono wave file and write out json text files
        '''
        self.logMsg("Start Text Conversion")
        
        if self.audioPath is None:
            messagebox.showinfo("AudioText", "No audio file selected. File Select an Audio File.")
            return
            
        if self.modelPath.get() == "":
            messagebox.showinfo("AudioText", "No model file selected. File Select a model path.")
            return         
            
        # convert mp3 file to wav
        if self.audioExt == '.mp3':
            self.logMsg("convert mp3 to wav")
            try:
                # create file name for stereo wav file
                self.wavStereoFile = self.audioPath + "_stereo.wav"
                sound = AudioSegment.from_mp3(self.audioPath + self.audioExt)
#                cut = sound[120 * 1000:180 * 1000]
#                cut.export(self.wavStereoFile, format="wav")
                sound.export(self.wavStereoFile, format="wav")
                self.logMsg("Finished exporting WAV file:{}".format(self.wavStereoFile))
            except Exception as e:
                messagebox.showinfo("Error Converting MP3 To WAV", e)
                return
        
        # see if the user opened a wav file which skipped the mp3 to wav conversion step
        if self.audioExt == '.wav':
            self.wavStereoFile = self.audioFileName.get()
            
        # if wav file is stereo then convert it to mono
        self.logMsg("convert stereo wav to mono wav")
        # read input file and write mono output file
        try:
            # open the input and output files
            inFile = wave.open(self.wavStereoFile,'rb')
            splitFile = os.path.splitext(self.wavStereoFile)
            self.stereoPath = splitFile[0]
            self.stereoExt = splitFile[1]
            self.monoWav = self.stereoPath + "_Mono" + self.stereoExt
            outFile = wave.open(self.monoWav,'wb')
            # force mono
            outFile.setnchannels(1)
            # set output file like the input file
            outFile.setsampwidth(inFile.getsampwidth())
            outFile.setframerate(inFile.getframerate())
            # read
            soundBytes = inFile.readframes(inFile.getnframes())
            print("frames read: {} length: {}".format(inFile.getnframes(),len(soundBytes)))
            # convert to mono and write file
            monoSoundBytes = audioop.tomono(soundBytes, inFile.getsampwidth(), 1, 1)
            outFile.writeframes(monoSoundBytes)
            self.logMsg("Finished exporting Mono WAV file:{}".format(self.monoWav))
        except Exception as e:
            messagebox.showinfo("Error Converting WAV stereo To WAV Mono", e)
            return
        finally:
            inFile.close()
            outFile.close()
        
        # convert mono wav to text
        try:
            self.logMsg("convert mono wav to json text")
            inFileName = self.monoWav
            splitFile = os.path.splitext(inFileName)
            self.jsonPath = splitFile[0]
            outfileResults = self.jsonPath + "-Results.json"
            outfileText = self.jsonPath + "-Text.json"
            
            self.logMsg("Open WAV file.")
            wf = wave.open(inFileName, "rb")

            # initialize a str to hold results
            results = []
            textResults = []

            # build the model and recognizer objects.
            self.logMsg("Build language model (this takes awhile).")
            model = Model(self.modelPath.get())
            self.logMsg("Start recognizer.")
            recognizer = KaldiRecognizer(model, wf.getframerate())
            recognizer.SetWords(True)
            self.logMsg("Process audio file.")
            while True:
                data = wf.readframes(4000)
                if len(data) == 0:
                    break
                if recognizer.AcceptWaveform(data):
                    recognizerResult = recognizer.Result()
                    # convert the recognizerResult string into a dictionary  
                    resultDict = json.loads(recognizerResult)
                    # save the entire dictionary in the list
                    results.append(resultDict)
                    # save the 'text' value from the dictionary into a list
                    textResults.append(resultDict.get("text", ""))
                    self.logMsg(resultDict.get("text", ""))
                  
            # process "final" result
            resultDict = json.loads(recognizer.FinalResult())
            results.append(resultDict)
            textResults.append(resultDict.get("text", ""))

            # write results to a file
            with open(outfileResults, 'w') as output:
                print(json.dumps(results, indent=4), file=output)
                self.logMsg("Finished exporting json results file:{}".format(outfileResults))

            # write text portion of results to a file
            with open(outfileText, 'w') as output:
                print(json.dumps(textResults, indent=4), file=output)
                self.logMsg("Finished exporting json text file:{}".format(outfileText))
            
        except Exception as e:
            messagebox.showinfo("Error Converting mono WAV stereo to json text file", e)
            return

        
root = Tk()
app = Window(root)
root.wm_title("AudioText")
root.geometry("600x600")
root.mainloop()
