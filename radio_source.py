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
from gnuradio.fft import logpwrfft

import osmosdr

import time

from morse_decoder import morse_decoder

from matplotlib import pyplot as plt
import numpy as np

import struct

import thread



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

        self.logpwrfft_x_0 = logpwrfft.logpwrfft_c(
               sample_rate=samp_rate,
               fft_size=fft_size,
               ref_scale=2,
               frame_rate=20,
               avg_alpha=1.0,
               average=False,
        )
        
        self.msgq_out = blocks_message_sink_0_msgq_out = gr.msg_queue(2)
        
        self.blocks_message_sink_0 = blocks.message_sink(gr.sizeof_float*fft_size, blocks_message_sink_0_msgq_out, False)
        


        #### Connections ####
        if sourceType == 0:
            self.connect((self.rtl2832_source, 0), (self.logpwrfft_x_0, 0))
        
        elif sourceType == 1:
            self.connect((self.blocks_wavfile_source_0, 1), (self.block_throttle_im, 0))
            self.connect((self.blocks_wavfile_source_0, 0), (self.block_throttle_real, 0))
            self.connect((self.block_throttle_real, 0), (self.block_wav_float_to_complex, 0))
            self.connect((self.block_throttle_im, 0), (self.block_wav_float_to_complex, 1))
            self.connect((self.block_wav_float_to_complex, 0), (self.logpwrfft_x_0, 0))

        self.connect((self.logpwrfft_x_0, 0), (self.blocks_message_sink_0, 0))



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
    
    fft_size = 2048 #Should be a power of 2
    samp_rate = 250e3
    
    #middle_freq = 90.3e6 #NRK P1
    middle_freq = 144.400e6 #Vassfjellet
    #middle_freq = 96.3e6
    gain = 30
    bandwidth = 250e3
    
    morse_evaluation_time_range = 10#seconds
    buffer_size_max = (int)(samp_rate / fft_size) * morse_evaluation_time_range
    
    
    #### Options set up ####
    parser = OptionParser(option_class=eng_option, usage="%prog: [options]")
    parser.add_option("-f","--file", dest="filename", help="Use .wav FILE as source", metavar="FILE")
    parser.add_option("-F","--middle_frequency", type="int", dest="freq",  help="Set middle frequency (Hz)")
    #TODO add more options


    #### Options parsing ####
    (options, args) = parser.parse_args()
    
    if (options.filename):
        sourceType = 1
        filename = options.filename
        print "Source file: ", filename
    elif (options.freq):
        middle_freq = options.freq



    print "Middle frequency: ", middle_freq

    #### Radio set up ####
    radio = radio_input(fft_size, samp_rate, middle_freq, gain, bandwidth, sourceType, filename)

    radio.start()
    
    decoder = morse_decoder(fft_size, buffer_size_max);

    
    fft_data = []
    fft_feeding_frames = []
    floats = []


    #### fft feeding loop ####
    try:
        while True:
            #time.sleep(0.1)
            
            
            fft=radio.msgq_out.delete_head().to_string() # this indeed blocks
            
            def feedData ():
                fft_feeding_frames = []
                floats=[]
                if (len(fft)>fft_size):
                    for i in range(0,len(fft),4):
                        floats.append(struct.unpack_from('f',fft[i:i+4]))
                    #print "got",len(floats), "floats; FFT size is", radio.fft_size
                    i=0
            
        
                    while i<len(floats): # gnuradio might sometimes send multiple vectors at once
                        frame=floats[i:i+radio.fft_size]
                        #print "test of length frame ", len(frame)
                        fft_feeding_frames.append(frame)
                        i+=radio.fft_size
        
                    if (len(fft_feeding_frames)>0):
                        decoder.feed_input(fft_feeding_frames)
            
            #thread.start_new_thread(feedData, ())
            feedData()



    except KeyboardInterrupt: #catch control-c to leave loop
            pass




    #Finish doing stuff here:
    print ""
    print "Shutting down!"
    radio.stop()
    radio.wait()




