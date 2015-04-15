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

#line, = []


#### skeleton for the morse decoder class ####
class morse_decoder ():
    
    dataPerFrame = 0
    
    frame_buffer = []
    
    buffer_size_max = 1200
    
    start_animate = False
    
    
    
    
    def __init__(self, dataPerFrame = 4096, buffer_size_max = 1200):
        self.dataPerFrame = dataPerFrame
        self.buffer_size_max = buffer_size_max
        print "self.buffer_size_max ", self.buffer_size_max
    
    
    def feed_input(self, input):
        
        if len(input[0]) == self.dataPerFrame:
            
        
            if (len(self.frame_buffer) > 200 and self.start_animate == False):
                self.start_animate = True
                
                
        
                # First set up the figure, the axis, and the plot element we want to animate
                fig = plt.figure()
                ax = plt.axes(xlim=(0, len(self.frame_buffer[0])), ylim=(0, 140))
                line, = ax.plot([], [], lw=2)

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
    
                anim = animation.FuncAnimation(fig, animate, init_func=init, frames=len(self.frame_buffer[0]), interval=200, blit=True)
        
                plt.show()

            elif self.start_animate == False:
                print "recieved ", len(input), " frames", len(self.frame_buffer)
                self.frame_buffer.extend(input)



        
        else:
            print "ERROR: wrong dataPerFrame size", len(input), " vs. ", self.dataPerFrame

#    # initialization function: plot the background of each frame
#    def init_animation(self, line):
#        line.set_data([], [])
#        return line,
#
#    # animation function.  This is called sequentially
#    def animate(self, i):
#        x = []
#        for u in range(0, len(fftts[0])):
#            x.append(u)
#            y = fftts[i%len(fftts)]
#            line.set_data(x, y)
#        return line,
#
#    def animate_spectrum(self, fftts):
#        # First set up the figure, the axis, and the plot element we want to animate
#        
#        fig = plt.figure()
#        ax = plt.axes(xlim=(0, 200), ylim=(0, 140))
#        line, = ax.plot([], [], lw=2)
#        
#        ifunc=self.init_animation(line)
#        
#        anim = animation.FuncAnimation(fig, self.animate, init_func = ifunc, frames=len(fftts[0]), interval=60, blit=True)





