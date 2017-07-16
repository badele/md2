# coding: utf-8

"""Usage: midi.py sonicpi [--played_at_bpm=<bpm>] FILE
       midi.py text FILE

Convert FILE to other format

Arguments:
    FILE            Midi filename

Options:
    -h, --help      Help

"""

import midi
from collections import OrderedDict

from docopt import docopt
 
def analyseMidiFile(filename):

    notes = [":C", ":Cs", ":D", ":Ds", ":E", ":F", ":Fs", ":G", ":Gs", ":A", ":As", ":B"]
    
    pattern = midi.read_midifile(filename)

    # Search BPM
    timeinfo={}
    timeinfo['resolution'] = pattern.resolution

    for midinfo in pattern[0]:
        if type(midinfo) == midi.TimeSignatureEvent:
            timeinfo['numerator'] = midinfo.data[0]
            timeinfo['denominator'] = 2 ** midinfo.data[1]
            timeinfo['tick_per_metronome'] = midinfo.data[2]
            timeinfo['ppqn'] = timeinfo['resolution'] / timeinfo['numerator']
            timeinfo['ntquater'] = timeinfo['resolution'] / timeinfo['numerator']

            # If not 4/4 partition, raise exception
            if timeinfo['numerator'] != 4 and timeinfo['denominator'] != 4:
                raise Exception("Cannot convert this midi file (numerator/denominator) compatibility")

        if type(midinfo) == midi.SetTempoEvent:
            tempo = midinfo.data[0] * 256**2 + midinfo.data[1] * 256 + midinfo.data[2]
            timeinfo['bpm'] = 60000000 / tempo
            timeinfo['tempo'] = tempo
            timeinfo['tick_time'] = tempo / float(timeinfo['resolution']) * timeinfo['bpm']/60.0
            # Ticks
            timeinfo['ndwhole'] = timeinfo['ntquater'] * 8
            timeinfo['nwhole'] = timeinfo['ntquater'] * 4
            timeinfo['nminim'] = timeinfo['ntquater'] * 2
            timeinfo['neighth'] = timeinfo['ntquater'] / 2
            timeinfo['nsixteenth'] = timeinfo['ntquater'] / 4
            timeinfo['n32th'] = timeinfo['ntquater'] / 8
            timeinfo['n64th'] = timeinfo['ntquater'] / 16
            # duration
            timeinfo['ddwhole'] = timeinfo['ndwhole'] * timeinfo['tick_time']
            timeinfo['dwhole'] = timeinfo['nwhole'] * timeinfo['tick_time']
            timeinfo['dminim'] = timeinfo['nminim'] * timeinfo['tick_time']
            timeinfo['dquater'] = timeinfo['ntquater'] * timeinfo['tick_time']
            timeinfo['deighth'] = timeinfo['neighth'] * timeinfo['tick_time']
            timeinfo['dsixteenth'] = timeinfo['nsixteenth'] * timeinfo['tick_time']
            timeinfo['d32th'] = timeinfo['n32th'] * timeinfo['tick_time']
            timeinfo['d64th'] = timeinfo['n64th'] * timeinfo['tick_time']

    # Search track with the most notes
    indexes=[]
    for info in pattern:
        indexes.append(len(info))

    m = max(indexes)
    smax = [i for i, j in enumerate(indexes) if j == m][0]

    # Parse track
    absticks = 0
    timelines = OrderedDict()
    currentnotes = {}

    for track in pattern[smax]:
        if type(track) == midi.events.NoteOnEvent or type(track) == midi.events.NoteOffEvent:
            noteidx = track.data[0]
            noteinoct = track.data[0] % 12
            notename = notes[noteinoct]
            octave = track.data[0]/12
            idx = "%(notename)s%(octave)s" % locals()
            absticks += track.tick


            if type(track) == midi.events.NoteOnEvent:

                # Store first tick note
                if 'tick_start' not in timeinfo:
                    timeinfo['tick_start'] = absticks

                if absticks < timeinfo['tick_start']:
                    timeinfo['tick_start'] = absticks

                # Add note
                noteinfo = {}
                noteinfo['note'] = noteidx
                noteinfo['notename'] = idx
                noteinfo['tick_start'] = absticks

                if absticks not in timelines:
                    tnotes = OrderedDict()
                    timelines[absticks] = tnotes

                timelines[absticks][noteidx] = noteinfo
                if noteidx not in currentnotes:
                    currentnotes[noteidx] = []
                currentnotes[noteidx].append(absticks)


            if type(track) == midi.events.NoteOffEvent:
                # Store last tick note
                if 'tick_stop' not in timeinfo:
                    timeinfo['tick_stop'] = absticks

                if absticks > timeinfo['tick_stop']:
                    timeinfo['tick_stop'] = absticks

                tickpos = currentnotes[noteidx].pop(0)
                timelines[tickpos][noteidx]['tick_stop'] = absticks

    return (timeinfo, timelines)

def convert2SonicPi(timeinfo, timelines, opts):

    uniqtime = {}

    # Add in uniqtime duration
    microseconds = 1000000.0

    uniqtime[timeinfo['ddwhole']] = 'ddwhole'
    uniqtime[timeinfo['dwhole']] = 'dwhole'
    uniqtime[timeinfo['dminim']] = 'dminim'
    uniqtime[timeinfo['dquater']] = 'dquater'
    uniqtime[timeinfo['deighth']] = 'deighth'
    uniqtime[timeinfo['dsixteenth']] = 'dsixteenth'
    uniqtime[timeinfo['d32th']] = 'd32th'
    uniqtime[timeinfo['d64th']] = 'd64th'
    
    # Check if we can play in Sonic PI
    for t in timelines:
        durations = OrderedDict()
        for n in timelines[t]:
            durations[timelines[t][n]['tick_stop']] = timelines[t][n]['tick_stop']

        if len(durations) > 1:
            raise Exception("Cannot play this track to Sonic PI, not same duration")

    # Analyse if we play with play_pattern_timed or play function
    alllines = []
    playpattern = []
    for t in timelines:
        if len(timelines[t]) == 1:
            playpattern.append(timelines[t].items()[0][1])
        else:
            if len(playpattern)>0:
                info = {'type': 'play_pattern_timed', 'data':playpattern}
                alllines.append(info)
                playpattern=[]

            play = []
            for n in timelines[t]:
                play.append(timelines[t][n])

            info = {'type': 'play', 'data':play}
            alllines.append(info)

    if len(playpattern)>0:
        info = {'type': 'play_pattern_timed', 'data': playpattern}
        alllines.append(info)

    # Export to Sonic PI
    quater_insecond = (timeinfo['tick_time']*timeinfo['ntquater']/microseconds)
    vars = "# Converted from midi file with sonic-pi-tools\n"
    vars += "# https://github.com/badele/sonic-pi-tools\n"
    vars += "#\n"
    vars += "# -- MIDI INFO  --\n"
    vars += "# TEMPO           = %s µs / %s bpm\n" % (timeinfo['tempo'], timeinfo['bpm'])
    vars += "# RESOLUTION      = %s\n" % timeinfo['resolution']
    vars += "# TICK TIME       = %s µs\n" % timeinfo['tick_time']
    vars += "# Quater nb tick  = %s\n" % timeinfo['ntquater']
    vars += "# Quater time     = %s s\n" % quater_insecond
    vars += "\n"

    if opts['--played_at_bpm']:
        vars += "dquater=%s\n" % (quater_insecond*(float(opts['--played_at_bpm'])/timeinfo['bpm']))
        code = "# Played at %s BPM\n" % opts['--played_at_bpm']
    else:
        vars += "dquater=%s\n" % quater_insecond
        code = "\nuse_bpm %s\n" % timeinfo['bpm']

    code += "\nuse_synth :piano\n"
    code += "live_loop :play do\n"

    currenttick = 0
    for pattern in alllines:
        if pattern['type'] == 'play_pattern_timed':
            firstnote = pattern['data'][0]
            pauseduration = (firstnote['tick_start'] - currenttick) * timeinfo['tick_time']
            if pauseduration > 0:
                if pauseduration > 0 and pauseduration not in uniqtime:
                    uniqtime[pauseduration] = "d%s" % (len(uniqtime) + 1)

                code += "\n  sleep %s\n" % uniqtime[pauseduration]
                currenttick = firstnote['tick_stop']
            else:
                code += "\n"


            notes = "["
            times = "["
            for n in pattern['data']:
                noteduration = (n['tick_stop'] - n['tick_start']) * timeinfo['tick_time']
                pauseduration = (n['tick_start'] - currenttick) * timeinfo['tick_time']

                if noteduration > 0 and noteduration not in uniqtime:
                    uniqtime[noteduration] = "d%s" % (len(uniqtime) + 1)

                if pauseduration > 0 and pauseduration not in uniqtime:
                    uniqtime[pauseduration] = "d%s" % (len(uniqtime) + 1)

                if pauseduration>0:
                    notes += 'nil,'
                    times += "%s," % uniqtime[pauseduration]


                notes += "%s," % n['notename']
                times += "%s," % uniqtime[noteduration]
                currenttick = n['tick_stop']


            notes = "%s]" % notes[:-1]
            times = "%s]" % times[:-1]
            code += "  play_pattern_timed %s, %s\n" % (notes, times)
        else:
            firstnote = pattern['data'][0]
            noteduration = (firstnote['tick_stop'] - firstnote['tick_start']) * timeinfo['tick_time']
            pauseduration = (firstnote['tick_start'] - currenttick) * timeinfo['tick_time']
            if pauseduration > 0:
                if pauseduration not in uniqtime:
                    uniqtime[pauseduration] = "d%s" % (len(uniqtime) + 1)

                code += "\n  sleep %s\n" % uniqtime[pauseduration]
            else:
                code += "\n"


            notes = ""
            for n in pattern['data']:
                notes += "%s," % n['notename']
            code += "  play [%s]\n" % notes[:-1]

            code += "  sleep %s\n" % uniqtime[noteduration]
            currenttick = n['tick_stop']

    factor = {'ddwhole': "8*dquater", 'dwhole': "4*dquater",'dminim': "2*dquater", 'deighth': "dquater/2",'dsixteenth': "dquater/4",'d32th': "dquater/8",'d64th': "dquater/16"}
    for key, value in uniqtime.items():
        if value != 'dquater':
            try:
                duration_idx = int(value[1:])
                duration = key/microseconds / float(quater_insecond)
                if duration > 0:
                    vars += "d%s=%s*dquater\n" % (duration_idx,duration)
                else:
                    vars += "d%s=dquater/%s\n" % (duration_idx,duration)
            except:
                vars += "%s=%s\n" % (value,factor[value])

    code += "  stop 3\n"
    code += "end"

    code = "%s%s" % (vars, code)
    return code


if __name__ == '__main__':
    opts = docopt(__doc__)

    if opts['sonicpi']:
        print opts['FILE']
        (timeinfo, timelines) = analyseMidiFile(opts['FILE']) 
        print convert2SonicPi(timeinfo, timelines, opts)