#TEST CODE

import matplotlib
matplotlib.use('TKAgg')

import numpy as np
import time
import morseutility as mu
from scipy.signal import wiener
from scipy.signal import butter, lfilter, freqz
#144 vassfjellet
from scipy.fftpack import fft
from scipy.io import wavfile
#from utility import pcm2float
from matplotlib import animation



import scipy.io

import matplotlib.pyplot as plt

def appendFourierTimeSeries(buffer):
	return 20*np.log10(np.abs(np.fft.rfft(buffer)))

def findUniques(array):
	uniques = []
	for i in range(0, len(array)):
		if(not (array[i] in uniques)):
			uniques.append(array[i])
	return uniques


def findAverage(signal):
	sum = 0
	for i in range(0, len(signal)):
		sum+=signal[i]
	return sum/len(signal)


#Malfunctioning
def identifyMorseFrequency(ffttimeseries):
	avg = findAverage(ffttimeseries[0]) #define normal state
	print avg
	peak = 30 #define what is a peak
	freqArray = []
	avg = []
	temparray = []
	highest = [0]*len(ffttimeseries[0])
	for i in range(0, len(ffttimeseries)):
		for u in range(0, len(ffttimeseries[i])):
			temparray.append(ffttimeseries[i][u])
			if(ffttimeseries[i][u]>highest[u]):
				highest[u]=ffttimeseries[i][u]
		avg.append(findAverage(temparray))
		temparray=[]
	for i in range(0, len(avg)):
		if((highest[i]-avg[i])>peak):
			#print highest[i], avg[i]
			freqArray.append(i)
	print avg[230], highest[230]
	print freqArray
	uniques = findUniques(freqArray)
	uniques.sort()
	simpUniques = []
	idxMin = 0
	for i in range(1, len(uniques)):
		#If current element -1 equals the previous element, we still have a sequence
		if((uniques[i]-1) == uniques[i-1]):
		        if(i == (len(uniques)-1)):
		                simpUniques.append(sum(uniques[idxMin:i+1])/(i+1 - idxMin))

		#If current element -1 differs from previous element, we have a possible new sequence
		else:
		        if((i - idxMin) == 0):
		                simpUniques.append(uniques[i])
		        else:
		                simpUniques.append(sum(uniques[idxMin:i])/(i - idxMin))

		        if(i == (len(uniques)-1)):  #Last element in array to be checked
		                simpUniques.append(uniques[i])

		        idxMin = i
	return simpUniques
	
#Returns True if Morse signal on given frequency
def isMorse(ffttimeseries, freq):
	fftavg = findAverage(ffttimeseries[:][freq])
	highcounter = 0
	isHigh = False
	isLow = True
	for i in range(0, len(ffttimeseries)):
		if(isPeak(ffttimeseries[i][freq], freq, fftavg) and isLow):
			highcounter +=1
			isHigh=True
			isLow=False
		if(not isPeak(ffttimeseries[i][freq], freq, fftavg)):
			isLow=True
		if(highcounter > 3):
			return True
	return False
	
def isPeak(fftdatapoint, freq, fftavg):
	peak = fftavg-0.25  #Won't work with isMorse()
	if(fftdatapoint>=peak):
		return True
	return False



#Writes a string of morse from the signal
def writeMorseString(ffttimeseries, freq):
	#starts by defining long/short
	highCounter = 0
	spaceCounter = 0
	spaceDefinition = 10000
	isHigh = 0
	lowest = 10000
	shortSig = lowest #initial definition of a short signal
	longSig = lowest*2 #initial definition of a long signal
	fftsum = 0
	for i in range(0, len(ffttimeseries)):
		fftsum+=ffttimeseries[i][freq]
	fftavg = fftsum/len(ffttimeseries)
	print "fftavg: ", fftavg
	filtered_fft = wiener(ffttimeseries[:,freq], 3)
	peakArray = []
	for i in range(0, len(ffttimeseries)):
		peakArray.append(isPeak(filtered_fft[i], freq, fftavg))
	for i in range(0, int(1*len(ffttimeseries))):
		if(peakArray[i]):
			highCounter +=1
			isHigh = 1
			if(spaceCounter!=0 and spaceCounter*2 < spaceDefinition):
				spaceDefinition = 3*spaceCounter
				print "space: ", spaceDefinition, "  ", i
			spaceCounter = 0
		elif(isHigh):
			if(highCounter<lowest):
				lowest=highCounter
				print lowest, " ", i
			highCounter = 0
			isHigh = 0
		if(not isHigh):	
			spaceCounter +=1
	shortSig = lowest #initial definition of a short signal
	longSig = lowest*2 #initial definition of a long signal
	print "Short sig is: ", shortSig, " Long sig is: ", longSig, "space is: ", spaceDefinition
	morsestring = ""
	highCounter = 0
	spaceCounter = 0

	for i in range(0, int(1*len(ffttimeseries))):
		if(peakArray[i]):
			highCounter +=1
			isHigh = 1
			if(spaceCounter >= spaceDefinition):
				morsestring += " "
			spaceCounter = 0
		elif(isHigh):
			if(highCounter>longSig):
				morsestring += "-"
			elif(highCounter < longSig):
				morsestring += "."
	
			highCounter = 0
			isHigh = 0
		if(not isHigh):	
			spaceCounter +=1
	return morsestring

def generatePlot(fftts, freq):
	fftsum = 0
	for i in range(0, len(fftts)):
		fftsum+=fftts[i][freq]
	fftavg = fftsum/len(fftts)
	peakArray = []
	filtered_fft = wiener(fftts[:,freq], 19)
	for i in range(0, len(fftts)):
		peakArray.append(isPeak(filtered_fft[i], freq, fftavg))
		#peakArray.append(filtered_fft[i])
		print filtered_fft[i]
	p = peakArray
	f = np.linspace(0, len(peakArray), len(p))
	plt.plot(f, p)
	



fs, data = scipy.io.wavfile.read("vassfjellet-la2vhf jp53eg_2015-03-08_SDRSharp_20150308_115801Z_144464kHz_IQ.wav")
print "fs: ", fs

Ts = 0.02
print data
data = data[:,1]

signalTime = int(len(data)/fs)
samplesPerFFT = fs*Ts
FFTiterations = int(signalTime/Ts)
print "Sigtime is: ",signalTime


window = scipy.signal.blackmanharris(samplesPerFFT,1)

fftts = []
for i in range(0, FFTiterations):
	fftts.append(appendFourierTimeSeries(window*data[i*samplesPerFFT:(samplesPerFFT+i*samplesPerFFT)]))


fftts=wiener(fftts,5)


'''
for i in range(0, len(fftts)):
	fftts[i]=wiener(fftts[i], 19)


for i in range(0, len(fftts[i])):
	if(isMorse(fftts,i)):
		print i
'''

sample = []
for i in range(0, len(fftts)):
	sample.append(fftts[i][230])
	

#sample = wiener(sample, 9)


# First set up the figure, the axis, and the plot element we want to animate
fig = plt.figure()
ax = plt.axes(xlim=(0, len(fftts[0])), ylim=(100, 140))
line, = ax.plot([], [], lw=2)

# initialization function: plot the background of each frame
def init():
    line.set_data([], [])
    return line,

# animation function.  This is called sequentially
def animate(i):
	x = []
	for u in range(0, len(fftts[0])):
		x.append(u)
	y = fftts[i%len(fftts)]
	line.set_data(x, y)
	return line,


#FILTER:################
'''
def butter_lowpass(cutoff,fs,order=5):
	nyq=0.5*fs
	normal_cutoff=cutoff/nyq
	b,a = butter(order,normal_cutoff,btype='low',analog=False)
	return b, a
	
def butter_lowpass_filter(data,cutoff,fs,order=5):
	b, a = butter_lowpass(cutoff,fs,order=order)
	y=lfilter(b,a,data)
	return y



order= 6
samplerate = int(1/Ts)
cutoff = 3

filterlists = []
templist = []
print len(fftts[1]), len(fftts)
for i in range(0,len(fftts[0])):
	for u in range(0,len(fftts)):
		templist.append(fftts[u][i])
	filterlists.append(templist)
	templist = []

print "length filterlists:(=amount of freqz) ", len(filterlists), "\n Length filterlists[0](time): ", len(filterlists[0])

for i in range(0,len(fftts[0])):
	filterlists[i]=butter_lowpass_filter(filterlists[i], cutoff,samplerate, order)

for i in range(0,len(fftts)):
	for u in range(0,len(fftts[0])):
		fftts[i][u]=filterlists[u][i]
		
'''
#########################   10911

# call the animator.  blit=True means only re-draw the parts that have changed.
anim = animation.FuncAnimation(fig, animate, init_func=init, frames=len(fftts[0]), interval=60, blit=True)





try:
	morsestring =  writeMorseString(fftts,230)
except:
	print "fgafgssfdg"

print "Morsestring is: ", morsestring

try:
	print "translated: ",mu.translateMorseString(morsestring)
except:
	print "hfsfg"

#generatePlot(fftts, 230)

#freqarray = identifyMorseFrequency(fftts)

print "for plot"

f = np.linspace(0, len(sample), len(sample))
plt.figure(1)	
plt.plot(f, sample)
f = np.linspace(0, len(fftts[0]), len(fftts[0]))
'''
for i in range(1,2):
	plt.figure(i+1)	
	plt.plot(f, fftts[3453])
'''

plt.show()

#print freqarray
'''

print morsestring
try:
	print mu.translateMorseString(morsestring)
except Exception as e:
	print "error translating", e

'''

