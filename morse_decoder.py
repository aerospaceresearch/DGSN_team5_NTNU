import matplotlib
matplotlib.use('TKAgg')

import numpy as np
import time
import morseutility as mu
from scipy.signal import wiener
from scipy.fftpack import fft
from scipy.io import wavfile
#from utility import pcm2float
from matplotlib import animation

import thread

import scipy.io

import matplotlib.pyplot as plt

#line, = []


#### skeleton for the morse decoder class ####
class morse_decoder ():
    
    dataPerFrame = 0
    
    frame_buffer = []
    
    buffer_size_max = 600
    
    buffer_iterator = 0
    i = 0
    
    start_animate = False
    
    step = 0
    
    f = 0
    
    
    def __init__(self, dataPerFrame = 1700, buffer_size_max = 40):
        self.dataPerFrame = dataPerFrame
        #self.buffer_size_max = buffer_size_max
        #print "self.buffer_size_max ", self.buffer_size_max
    
#    plt.ion()
#    pl, = plt.plot([0]*dataPerFrame)
#    plt.axis([0, dataPerFrame, -100, 70])
#    plt.draw()


    def feed_input(self, input):
        
        if len(input[0]) == self.dataPerFrame:
            
#            for i in range(0,len(input)):
#                del input [i][0:8]
#                del input [i][self.dataPerFrame-9:self.dataPerFrame-1]

            self.frame_buffer.extend(input)
            
            #print "recieved ", len(input[0]), " frames", len(self.frame_buffer)
            self.f = 392#self.find_freq_of_highest_peak(self.frame_buffer[self.buffer_iterator])
            
            if (len(self.frame_buffer)>40 and self.step >= 20):# and not self.start_animate):
                self.step=0
                self.start_animate = True
                thread.start_new_thread( self.decode_morse, () )
            #plt.show

            self.step+=1
            #print self.step
            #print self.frame_buffer[0]
            
#            self.pl.set_ydata(self.frame_buffer[self.buffer_iterator][0 : self.dataPerFrame])
#            plt.draw()



            if (len(self.frame_buffer) > 10000 and self.start_animate == False):
                # First set up the figure, the axis, and the plot element we want to animate
                fig = plt.figure()
                ax = plt.axes(xlim=(0, len(self.frame_buffer[0])), ylim=(0, 140))
                line, = ax.plot([], [], lw=2)
                
                self.start_animate = True
                
                # initialization function: plot the background of each frame
                def init():
                    line.set_data([], [])
                    return line,

                # animation function.  This is called sequentially
                def animate(i):
                    x = []
                    for u in range(0, len(self.frame_buffer[0])):
                        x.append(u)
                    y = self.frame_buffer[i%len(self.frame_buffer)]
                    line.set_data(x, y)
                    return line,
    
                anim = animation.FuncAnimation(fig, animate, init_func=init, frames=len(self.frame_buffer[0]), interval=100, blit=True)
        
                plt.show()


            self.buffer_iterator += len(input)

        else:
            print "ERROR: wrong dataPerFrame size", len(input), " vs. ", self.dataPerFrame
                
                
        overflow = len(self.frame_buffer) - self.buffer_size_max
        if (overflow > 0) :
            del self.frame_buffer[0:overflow]
            self.buffer_iterator -= overflow


    def find_freq_of_highest_peak(self, frame):
        f = frame.index(max(frame))
        return f

    #Writes a string of morse from the signal
    def writeMorseString(self, ffttimeseries, freq):
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
        filtered_fft = ffttimeseries[:,freq]#wiener(ffttimeseries[:,freq], 1)
        fftavg = (min(filtered_fft) - max(filtered_fft)) / 2
        print "High/Low threshold = ", fftavg
        sample=filtered_fft
        peakArray = []
#        f = np.linspace(0, len(sample), len(sample))
#        plt.figure(1)
#        plt.plot(f, sample)
        for i in range(0, len(ffttimeseries)):
            peakArray.append(isPeak(filtered_fft[i], freq, fftavg))
        #print filtered_fft
        #print peakArray
        for i in range(0, int(1*len(ffttimeseries))):
            if(peakArray[i]):
                highCounter +=1
                isHigh = 1
                if(spaceCounter!=0 and spaceCounter*2 < spaceDefinition):
                    spaceDefinition = 3*spaceCounter
                    #print "space: ", spaceDefinition, "  ", i
                spaceCounter = 0
            elif(isHigh):
                if(highCounter<lowest):
                    lowest=highCounter
                    #print lowest, " ", i
                highCounter = 0
                isHigh = 0
            if(not isHigh):
                spaceCounter +=1
        shortSig = 2#lowest #initial definition of a short signal
        longSig = 4#lowest*2 #initial definition of a long signal
        spaceDefinition = 6
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

    def decode_morse (self):
        morsestring = self.writeMorseString(np.array(self.frame_buffer), self.f);
        plt.show()
        print "Buffer size = ", len(self.frame_buffer), " of ", self.buffer_size_max
        print morsestring
        print mu.translateMorseString(morsestring)
        print "Looking at relative freq = ", self.f
        print ""


def isPeak(fftdatapoint, freq, fftavg):
    peak = fftavg#-0.25  #Won't work with isMorse()
    if(fftdatapoint>=peak):
        return 1
    return 0













