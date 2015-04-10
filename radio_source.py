#!/usr/bin/env python

##################################################
# A software defined radio source feeding fft frames to a morse decoder - v0.1
# Supports rtl2832 sources and .wav file sources
# DGSN Trondheim 'Team 5' - NTNU EiT 2015
# Created: Wed Mar 18 15:43:18 2015
##################################################

from gnuradio import blocks
from gnuradio import eng_notation
from gnuradio import gr
from gnuradio.eng_option import eng_option
from gnuradio.filter import firdes

from gnuradio import audio
from gnuradio import filter
from gnuradio import analog

from optparse import OptionParser
from gnuradio.fft import window

from gnuradio import fft

import osmosdr

import time

from matplotlib import pyplot as plt
import numpy as np


#### skeleton for the morse decoder class ####
class morse_decoder ():
    
    def __init__(self, dataPerFrame = 4096):
        self.dataPerFrame = dataPerFrame
    

    def feed_input(self, input):
        
        
        if len(input) == self.dataPerFrame:
            print "recieved frame of length ", len(input)
        else:
            print "ERROR: wrong dataPerFrame size" + len(input) + " vs. " + dataPerFrame


#### The 'radio' class, created using gnuradio blocks ####
class radio_input(gr.top_block):
    
    def __init__(self, fft_size, samp_rate, middle_freq, gain, bandwidth, sourceType = 0, filename = ""):
        gr.top_block.__init__(self, "Top Block")
        
        #### Variables ####
        
        self.fft_size = fft_size
        
        self.samp_rate = samp_rate
        self.middle_freq = middle_freq
        self.gain = gain
        self.bandwidth = bandwidth
        
        #### Blocks ####
        
        if sourceType == 0: #rtl2832 radio source
            self.rtl2832_source = osmosdr.source( args="numchan=" + str(1) + " " + "" )
            self.rtl2832_source.set_clock_source("gpsdo", 0)
            self.rtl2832_source.set_sample_rate(samp_rate)
            self.rtl2832_source.set_center_freq(middle_freq, 0)
            self.rtl2832_source.set_freq_corr(0, 0)
            self.rtl2832_source.set_dc_offset_mode(0, 0)
            self.rtl2832_source.set_iq_balance_mode(0, 0)
            self.rtl2832_source.set_gain_mode(False, 0)
            self.rtl2832_source.set_gain(gain, 0)
            self.rtl2832_source.set_if_gain(20, 0)
            self.rtl2832_source.set_bb_gain(20, 0)
            self.rtl2832_source.set_antenna("", 0)
            self.rtl2832_source.set_bandwidth(bandwidth, 0)
                
        elif sourceType == 1 and filename: #wave file source

            self.blocks_wavfile_source_0 = blocks.wavfile_source(filename, False)
            self.samp_rate = self.blocks_wavfile_source_0.sample_rate
            print "Sample rate set to ", samp_rate
            self.block_wav_float_to_complex = blocks.float_to_complex(1)
            self.block_throttle_real = blocks.throttle(gr.sizeof_float*1, samp_rate,True) #throttles reading from the wav file to simulate real time radio
            self.block_throttle_im = blocks.throttle(gr.sizeof_float*1, samp_rate,True)

                
        self.stream_to_vector_block = blocks.stream_to_vector(gr.sizeof_gr_complex*1, fft_size)
        self.fft_block = fft.fft_vcc(fft_size, True, (window.blackmanharris(fft_size)), True, 1)
        self.block_fft_complex_to_float = blocks.complex_to_float(fft_size)
        
        self.fft_sink_real = blocks.vector_sink_f(fft_size)
        #self.fft_sink_im = blocks.vector_sink_f(fft_size) # Q part of the I/Q signal, currently not used
        

        #### Connections ####
        
        if sourceType == 0:
             self.connect((self.rtl2832_source, 0), (self.stream_to_vector_block, 0))

        elif sourceType == 1:
            self.connect((self.blocks_wavfile_source_0, 1), (self.block_throttle_im, 0))
            self.connect((self.blocks_wavfile_source_0, 0), (self.block_throttle_real, 0))
            self.connect((self.block_throttle_real, 0), (self.block_wav_float_to_complex, 0))
            self.connect((self.block_throttle_im, 0), (self.block_wav_float_to_complex, 1))
            self.connect((self.block_wav_float_to_complex, 0), (self.stream_to_vector_block, 0))
        
        
        self.connect((self.stream_to_vector_block, 0), (self.fft_block, 0))
        self.connect((self.fft_block, 0), (self.block_fft_complex_to_float, 0))
        self.connect((self.block_fft_complex_to_float, 0), (self.fft_sink_real, 0))
        #self.connect((self.block_fft_complex_to_float, 1), (self.fft_sink_im, 0))



    def get_samp_rate(self):
        return self.samp_rate
    
    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.rtl2832_source.set_sample_rate(self.samp_rate)
    
    def get_middle_freq(self):
        return self.middle_freq
    
    def set_middle_freq(self, middle_freq):
        self.middle_freq = middle_freq
        self.rtl2832_source.set_center_freq(self.middle_freq, 0)
    
    def get_gain(self):
        return self.gain
    
    def set_gain(self, gain):
        self.gain = gain
        self.rtl2832_source.set_gain(self.gain, 0)
    
    def get_bandwidth(self):
        return self.bandwidth
    
    def set_bandwidth(self, bandwidth):
        self.bandwidth = bandwidth
        self.rtl2832_source.set_bandwidth(self.bandwidth, 0)



if __name__ == '__main__':
    
    
    #### Setting default values ####
    sourceType = 0
    filename = ""
    
    fft_size = 4096 #Should be a power of 2
    samp_rate = 250e3

    middle_freq = 90.3e6 #NRK P1
    #middle_freq = 144.450e6 #Vassfjellet
    gain = 10
    bandwidth = 250e3
    
    
    #### Options set up ####
    parser = OptionParser(option_class=eng_option, usage="%prog: [options]")
    parser.add_option("-f","--file", dest="filename", help="Use .wav FILE as source", metavar="FILE")
    #TODO add more options


    #### Options parsing ####
    (options, args) = parser.parse_args()
    
    if (options.filename):
        sourceType = 1
        filename = options.filename
    

    #### Radio set up ####
    radio = radio_input(fft_size, samp_rate, middle_freq, gain, bandwidth, sourceType, filename)

    radio.start()
    
    decoder = morse_decoder(radio.fft_size);

    
    fft_data = []

    ##### crude and dirty animation of fft spectrum for bug testing ####
#    firstAnimStage = True #animation code
#    plt.ion() #animation test code

    #### fft feeding loop ####
    try:
        while True:
            
            time.sleep(0.1) #doing this as it avoids some memory issues, a stream based solutions is probably better
            print "sink length ",len(radio.fft_sink_real.data())
            
            if len (radio.fft_sink_real.data()) > radio.fft_size:

                fft_data.extend(radio.fft_sink_real.data())
                
#                secondAnimStage = True #animation test code

                while (radio.fft_size < len(fft_data)):
                    
                    #### feed frame to decoder ####
                    decoder.feed_input(fft_data[0 : radio.fft_size])
                    
#                    if firstAnimStage: #animation test code
#                        firstAnimStage = False #animation test code
#                        pl, = plt.plot(fft_data[0 : radio.fft_size]) #animation test code
#                    elif secondAnimStage: #animation test code
#                        secondAnimStage = False #animation test code
#                        pl.set_ydata(fft_data[0 : radio.fft_size]) #animation test code
#                        plt.draw() #animation test code

                    del fft_data[0 : radio.fft_size]
            
                radio.fft_sink_real.reset()


    except KeyboardInterrupt: #catch control-c to leave loop
            pass

    #Finish doing stuff here:
    print ""
    print "Shutting down!"
    radio.stop()
    radio.wait()


