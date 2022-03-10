from tkinter import *
from tkinter import filedialog
import mutagen
from pygame import mixer
import os
import random
import time

class Player:#TODO filtering
	def __init__(self, root):
		self.root = root
		self.frequency = 0
		self.playing = False
		self.length = 0
#		iconpath = "/home/robert/data/songs/MusicPipe.ico"
#		self.root.iconbitmap("@"+iconpath)
		"""
		icon_image = PhotoImage(file=iconpath)
		print("icon_image =", icon_image)
		icon_label = Label(image=icon_image)
		print ("icon_label =", icon_label)
		assert icon_label.master is self.root
		print("about to fail..")
		self.root.iconwindow(icon_label)
		"""
		self.root.geometry("1000x300")
		self.root.title("Music Pipe")
#		self.root.iconbitmap("@/home/robert/data/songs/MusicPipe.xbm")

		#the things with "self." are dynamic, and need to be refrenced other places

		#current song
		buttonFrame = LabelFrame(self.root, text="Current Song", font=("times new roman",15,"bold"), bg="grey", fg="white", bd=5, relief=GROOVE)
		buttonFrame.pack(fill=X)
		volume = Entry(buttonFrame, )
		volume.pack(side=LEFT)
		buttonBackward = Button(buttonFrame, text="⏮", command=self.backward, width=1, height=1, font=("times new roman",16,"bold"), fg="black", bg="grey")
		buttonBackward.pack(side=LEFT)
		self.buttonPause = Button(buttonFrame, text="▶", command=self.togglePause, width=1, height=1, font=("times new roman",16,"bold"), fg="black", bg="grey")
		self.buttonPause.pack(side=LEFT)
		buttonForward = Button(buttonFrame,text="⏭", command=self.forward, width=1, height=1, font=("times new roman",16,"bold"), fg="black", bg="grey")
		buttonForward.pack(side=LEFT)
		self.songLabel = Label(buttonFrame, text="", width=35, font=("times new roman",24,"bold"))
		self.songLabel.pack(side=LEFT, fill=X, expand=True)

		#scrubber
		self.scrubber = Scale(self.root, command=self.scrub, label="00:00/00:00", from_=0, to=10, orient=HORIZONTAL, showvalue=False)
		self.scrubber.pack(fill=X)

		#queue
		queueFrame = LabelFrame(self.root, text="Queue", font=("times new roman",15,"bold"), bg="grey", fg="white", bd=5, relief=GROOVE)
		queueFrame.pack(side=LEFT, expand=True, fill=BOTH)
		scrol_y = Scrollbar(queueFrame, orient=VERTICAL)
		scrol_x = Scrollbar(queueFrame, orient=HORIZONTAL)
		self.queue = Listbox(queueFrame, xscrollcommand=scrol_x.set, yscrollcommand=scrol_y.set, selectbackground="gold", selectmode=MULTIPLE, font=("times new roman",12,"bold"), bg="silver", fg="navyblue", bd=5, relief=GROOVE)
		scrol_y.pack(side=RIGHT, fill=Y)
		scrol_x.pack(side=BOTTOM, fill=X)
		scrol_y.config(command=self.queue.yview)
		scrol_x.config(command=self.queue.xview)
		self.queue.pack(fill=BOTH, expand=True)

		#queue control
		queueControlFrame = Frame(self.root, bg="grey", bd=5, relief=GROOVE)
		queueControlFrame.pack(side=LEFT)
		buttonShuffle = Button(queueControlFrame,text="🔀", command=self.shuffle, width=1, height=1, font=("times new roman",16,"bold"), fg="black", bg="grey")
		buttonShuffle.pack()
		buttonAddAll = Button(queueControlFrame,text="⏪", command=self.addAll, width=1, height=1, font=("times new roman",16,"bold"), fg="black", bg="grey")
		buttonAddAll.pack()
		buttonAddSelected = Button(queueControlFrame,text="◀", command=self.addSelected, width=1, height=1, font=("times new roman",16,"bold"), fg="black", bg="grey")
		buttonAddSelected.pack()
		buttonRemoveAll = Button(queueControlFrame,text="⏩", command=self.removeAll, width=1, height=1, font=("times new roman",16,"bold"), fg="black", bg="grey")
		buttonRemoveAll.pack()
		buttonRemoveSelected = Button(queueControlFrame,text="▶", command=self.removeSelected, width=1, height=1, font=("times new roman",16,"bold"), fg="black", bg="grey")
		buttonRemoveSelected.pack()

		#playlist
		songsFrame = LabelFrame(self.root, text="Playlist", font=("times new roman",15,"bold"), bg="grey", fg="white", bd=5, relief=GROOVE)
		songsFrame.pack(side=LEFT, expand=True, fill=BOTH)
		scrol_y = Scrollbar(songsFrame, orient=VERTICAL)
		scrol_x = Scrollbar(songsFrame, orient=HORIZONTAL)
		self.playlist = Listbox(songsFrame, xscrollcommand=scrol_x.set, yscrollcommand=scrol_y.set, selectbackground="gold", selectmode=MULTIPLE, font=("times new roman",12,"bold"), bg="silver", fg="navyblue", bd=5, relief=GROOVE)
		scrol_y.pack(side=RIGHT, fill=Y)
		scrol_x.pack(side=BOTTOM, fill=X)
		scrol_y.config(command=self.playlist.yview)
		scrol_x.config(command=self.playlist.xview)
		self.playlist.pack(fill=BOTH, expand=True)

		#playlist control
		playlistControlFrame = Frame(self.root, bg="grey", bd=5, relief=GROOVE)
		playlistControlFrame.pack(side=LEFT)
		buttonImport = Button(playlistControlFrame, text="⭳", command=self.askPath, width=1, height=1, font=("times new roman",16,"bold"), fg="black", bg="grey")
		buttonImport.pack()

	def askPath(self):
		path = filedialog.askdirectory()
		if len(path) > 0:
			self.getSongs(path)

	def getSongs(self, path):
		self.playlist.delete(0, END)
		songs = []
		for root, subdirs, files in os.walk(path):
			for song in files:
				song = os.path.normpath(song)
				if song[-4:] == ".ogg":
					songs.append(os.path.join(root, song))
		for song in sorted(songs):
			self.playlist.insert(END, song)

	def playSong(self, song):
		global ScrubbingOffset
		ScrubbingOffset = 0
		songInfo = mutagen.File(song).info
		if songInfo.sample_rate != self.frequency:
			self.frequency = songInfo.sample_rate
			if mixer.get_init():
				mixer.quit()
			mixer.init(frequency=self.frequency)
		self.length = songInfo.length*1000
		self.scrubber.config(to=self.length)
		self.updateSongName(os.path.split(song)[1][:-4])
		mixer.music.load(song)
		mixer.music.play()
		self.buttonPause.config(text="⏸")
		self.playing = True

	def togglePause(self):
		if mixer.get_init():
			if mixer.music.get_busy():
				if self.playing:
					mixer.music.pause()
					self.buttonPause.config(text="▶")
					self.playing = False
				else:
					mixer.music.unpause()
					self.buttonPause.config(text="⏸")
					self.playing = True
				return
		self.incrementQueue()

	def backward(self):
		if mixer.get_init():
			global ScrubbingOffset
			ScrubbingOffset = -mixer.music.get_pos()
			mixer.music.rewind()

	def forward(self):
		if self.incrementQueue():
			self.buttonPause.config(text="⏸")
			self.playing = True
		else:
			mixer.music.stop()
			self.updateSongName("")
			self.buttonPause.config(text="▶")
			self.length = 0
			self.scrubber.config(to=0)
			self.playing = False

	def incrementQueue(self):
		global CheckBusy
		song = self.queue.get(0)
		if song != "":
			CheckBusy = True
			self.queue.delete(0)
			self.playSong(song)
			return True
		else:
			self.updateSongName("")
			self.buttonPause.config(text="▶")
			self.length = 0
			self.scrubber.config(to=0)
			self.playing = False
			CheckBusy = False
			return False

	def shuffle(self):
		songs = list(self.queue.get(0, END))
		random.shuffle(songs)
		self.queue.delete(0, END)
		for song in songs:
			self.queue.insert(END, song)

	def addAll(self):
		for song in self.playlist.get(0, END):
			self.queue.insert(END, song)

	def addSelected(self):
		for i in self.playlist.curselection():
			song = self.playlist.get(i)
			self.queue.insert(END, song)

	def removeAll(self):
		self.queue.delete(0, END)

	def removeSelected(self):
		for i in reversed(self.queue.curselection()):
			self.queue.delete(i)

	def scrub(self, pos):
		pos = int(pos)
		self.scrubber.config(label=posToTime(pos)+"/"+posToTime(self.length))
		global AutoScrub
		if AutoScrub:
			AutoScrub = False
		else:
			if mixer.music.get_busy():
				global ScrubbingOffset
				ScrubbingOffset = pos-mixer.music.get_pos()
				mixer.music.set_pos(pos/1000)

	def updateSongName(self, name):
		if name == "":
			self.root.title("Music Pipe")
		else:
			self.root.title(name)
		self.songLabel.config(text=name)

def posToTime(pos):
	pos /= 1000
	m = int(pos//60)
	s = int(pos%60)
	return f"{m}:{s:02n}"

def close():
	global ToClose
	global Root
	ToClose = True
	Root.quit()
	Root.destroy()

Root = Tk()
Root.protocol("WM_DELETE_WINDOW", close)

player = Player(Root)

ScrubbingOffset = 0
ToClose = False
CheckBusy = False
AutoScrub = False
while True:
	time.sleep(0.01)
	Root.update_idletasks()
	Root.update()

	if ToClose:
		mixer.quit()
		quit()

	if CheckBusy:
		if not mixer.music.get_busy():
			player.incrementQueue()

	if mixer.get_init():
		AutoScrub = True
		pos = mixer.music.get_pos() + ScrubbingOffset
		player.scrubber.set(pos)

