#!/usr/bin/env python
"""

"""
import sys
import time
import logging
import curses
import predict
import argparse
import radio
import satellites


SATELLITES = satellites.SATELLITES


GROUNDSTATION = (63.418, -10.399, 80) # lat (N), long (W), alt (meters)
MINELEVATION  =  0 # degrees
UPDATEINTERVAL = 0.2 # seconds between update

FREQADJUST = 100 # Hz to adjust when using arrow keys

EVALPASSES = 2 # number of passes to evaluate when searching for next good pass

LOGFILE = "tracklog.log"

# initialize logging
logging.basicConfig(
    filename=LOGFILE,
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s')


def writeline(string):
    sys.stdout.write("\r " + string + "                            ") # clear and print new line
    sys.stdout.flush()


def nextsat():
    transits = []
    i=0
    for tle, freq in SATELLITES:
        p = predict.transits(tle, GROUNDSTATION)
        for n in range(0,EVALPASSES):
            try:
                transit = p.next()
            except predict.PredictException, e:
                logging.warning("Satellite not scheduled. Reason: %s" % (e))
                break
            if(transit.peak()['elevation'] > MINELEVATION): # skip low transit
                transit = transit.above(MINELEVATION)
                if transit.start > time.time(): # skip old transit
                    transits.append([i, transit])
        i+=1
 
    # sort by max elevation
    transits = sorted(transits, key=lambda transit: transit[1].peak()['elevation'], reverse=True)

    # schedule nonoverlapping good events
    schedule = []
    for transit in transits:
        overlaps = False
        for event in schedule:
             # overlapping time
            if (transit[1].start >= event[1].start) and (transit[1].end <= event[1].end):
                overlaps = True
                break;
        if not overlaps:
            schedule.append(transit) 
    
    return min(schedule, key=lambda transit: transit[1].start)

def main(stdscr):

    recording = False
    levels = []

    # parse program arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--doppler", help="automatic correction of Doppler shift", action="store_true")
    args = parser.parse_args()

    stdscr.nodelay(1)

    while True:
        satid, transit = nextsat()
        tle, freq = SATELLITES[satid]
        freqadjust = 0
        aostime = time.strftime("%H:%M:%S", time.localtime(transit.start))
        lostime = time.strftime("%H:%M:%S", time.localtime(transit.end))
        logging.info("Scheduling %s at %s" % (tle[2:].split("\n")[0], aostime))


        while transit.end > time.time():
             # read key press and adjust freq
            c = stdscr.getch()
            if c == 258: # up arrow
                freqadjust -= FREQADJUST
            elif c == 259: # down arrow
                freqadjust += FREQADJUST
            elif c == 10: # enter key
                ra.tune(freq + freqadjust)

            now = time.time()
            observe = predict.observe(tle, GROUNDSTATION)
            name = observe['name'][2:]

            timeleft = transit.end - now
            minutes = int(timeleft / 60)
            seconds = int(timeleft - minutes * 60) 

            if transit.start > now: # waiting for upcoming satellite
                if recording: # stop recording
                    logging.info("LOS. Levels: %.3f/%.3f/%.3f" % (
                        min(levels),
                        sum(levels)/len(levels),
                        max(levels)
                    ))
                    levels = []
                    ra.los()
                    recording = False

                writeline("Waiting for %s AOS: %s, %s   %02.3f/%02.3f @ %d + %d" % (
                    name,
                    aostime,
                    "%03d:%02d" % (minutes, seconds),
                    observe['elevation'],
                    transit.peak()['elevation'],
                    freq,
                    freqadjust
                ))

            else:
                if args.doppler:
                    f = freq + observe['doppler']/100000000 * freq
                    ra.tune(f + freqadjust)
                else:
                    f = freq

                if not recording: # start recording
                    logging.info("AOS of %s at %d Hz for %.3f min (%.3f deg) " % (
                        name,
                        freq,
                        transit.duration()/60,
                        transit.peak()['elevation']))
                    ra.aos()
                    recording = True

                levels.append(float(ra.getlevel())) # gather statistics
                writeline("Tracking %s LOS: %s, %s   %02.3f/%02.3f @ %d + %d" % (
                    name,
                    lostime,
                    "%03d:%02d" % (minutes, seconds),
                    observe['elevation'],
                    transit.peak()['elevation'],
                    f,
                    freqadjust
                ))

            time.sleep(UPDATEINTERVAL)

if __name__ == "__main__":
    writeline("Initializing radio connection")
    logging.info("Starting up")
    ra = radio.radio()
    ra.init()
    ra.mode(ra.MODE_CWL)

    try: # graceful exit at Crtl+C
        curses.wrapper(main)
    except KeyboardInterrupt:
        ra.los()
        ra.close()
        logging.info("Exiting")
        print ""