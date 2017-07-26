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
    songinfo={}
    songinfo['resolution'] = pattern.resolution
    track_ids = []

    # Get MIDI information from track #0
    for midinfo in pattern[0]:
        if type(midinfo) == midi.TimeSignatureEvent:
            songinfo['numerator'] = midinfo.data[0]
            songinfo['denominator'] = 2 ** midinfo.data[1]
            songinfo['tick_per_metronome'] = midinfo.data[2]
            songinfo['ppqn'] = songinfo['resolution'] / songinfo['numerator']
            songinfo['ntquater'] = songinfo['resolution'] / songinfo['numerator']

            # If not 4/4 partition, raise exception
            if songinfo['numerator'] != 4 and songinfo['denominator'] != 4:
                raise Exception("Cannot convert this midi file (numerator/denominator) compatibility")

        if type(midinfo) == midi.SetTempoEvent:
            tempo = midinfo.data[0] * 256**2 + midinfo.data[1] * 256 + midinfo.data[2]
            songinfo['bpm'] = 60000000 / tempo
            songinfo['tempo'] = tempo
            songinfo['tick_time'] = tempo / float(songinfo['resolution']) * songinfo['bpm']/60.0
            # Ticks
            songinfo['ndwhole'] = songinfo['ntquater'] * 8
            songinfo['nwhole'] = songinfo['ntquater'] * 4
            songinfo['nminim'] = songinfo['ntquater'] * 2
            songinfo['neighth'] = songinfo['ntquater'] / 2
            songinfo['nsixteenth'] = songinfo['ntquater'] / 4
            songinfo['n32th'] = songinfo['ntquater'] / 8
            songinfo['n64th'] = songinfo['ntquater'] / 16
            # duration
            songinfo['ddwhole'] = songinfo['ndwhole'] * songinfo['tick_time']
            songinfo['dwhole'] = songinfo['nwhole'] * songinfo['tick_time']
            songinfo['dminim'] = songinfo['nminim'] * songinfo['tick_time']
            songinfo['dquater'] = songinfo['ntquater'] * songinfo['tick_time']
            songinfo['deighth'] = songinfo['neighth'] * songinfo['tick_time']
            songinfo['dsixteenth'] = songinfo['nsixteenth'] * songinfo['tick_time']
            songinfo['d32th'] = songinfo['n32th'] * songinfo['tick_time']
            songinfo['d64th'] = songinfo['n64th'] * songinfo['tick_time']

    # Parse track
    tracks = OrderedDict()
    for trackid, track in enumerate(pattern):
        if trackid == 0:
            continue

        absticks = 0
        currentnotes = {}
        track_ids.append(trackid)
        tracks[trackid] = {'title': '', 'notes': OrderedDict(), 'trackinfo': {}}

        eventidx = 0
        for track in pattern[trackid]:
            if type(track) == midi.TrackNameEvent:
                tracks[trackid]['title'] = track.text

            if type(track) == midi.events.NoteOnEvent or type(track) == midi.events.NoteOffEvent:
                noteidx = track.data[0]
                noteinoct = track.data[0] % 12
                notename = notes[noteinoct]
                octave = track.data[0]/12
                idx = "%(notename)s%(octave)s" % locals()
                absticks += track.tick


                if type(track) == midi.events.NoteOnEvent:

                    # Store first tick note
                    if 'tick_start' not in tracks[trackid]['trackinfo']:
                        tracks[trackid]['trackinfo']['tick_start'] = absticks

                    if absticks < tracks[trackid]['trackinfo']['tick_start']:
                        tracks[trackid]['trackinfo']['tick_start'] = absticks

                    # Add note
                    eventidx += 1
                    noteinfo = {}
                    noteinfo['eventidx'] = eventidx
                    noteinfo['note'] = noteidx
                    noteinfo['notename'] = idx
                    noteinfo['tick_start'] = absticks

                    if absticks not in tracks[trackid]['notes']:
                        tnotes = OrderedDict()
                        tracks[trackid]['notes'][absticks] = tnotes

                    tracks[trackid]['notes'][absticks][noteidx] = noteinfo

                    if noteidx not in currentnotes:
                        currentnotes[noteidx] = []
                    currentnotes[noteidx].append(absticks)


                if type(track) == midi.events.NoteOffEvent:
                    # Store last tick note
                    if 'tick_stop' not in tracks[trackid]['trackinfo']:
                        tracks[trackid]['trackinfo']['tick_stop'] = absticks

                    if absticks > tracks[trackid]['trackinfo']['tick_stop']:
                        tracks[trackid]['trackinfo']['tick_stop'] = absticks

                    tickpos = currentnotes[noteidx].pop(0)

                    # eventidx += 1
                    # tracks[trackid]['notes'][tickpos][noteidx]['eventidx'] = eventidx


                    tracks[trackid]['notes'][tickpos][noteidx]['tick_stop'] = absticks
                    duration = absticks - tracks[trackid]['notes'][tickpos][noteidx]['tick_start']
                    tracks[trackid]['notes'][tickpos][noteidx]['tick_duration'] = duration


    # Delete track with no datas
    for trackid in track_ids:
        if len(tracks[trackid]['notes'])==0:
            del tracks[trackid]

    return (songinfo, tracks)

def convert2SonicPi(songinfo, tracks, opts):

    uniqtime = {}

    # Add in uniqtime duration
    microseconds = 1000000.0

    uniqtime[songinfo['ddwhole']] = 'ddwhole'
    uniqtime[songinfo['dwhole']] = 'dwhole'
    uniqtime[songinfo['dminim']] = 'dminim'
    uniqtime[songinfo['dquater']] = 'dquater'
    uniqtime[songinfo['deighth']] = 'deighth'
    uniqtime[songinfo['dsixteenth']] = 'dsixteenth'
    uniqtime[songinfo['d32th']] = 'd32th'
    uniqtime[songinfo['d64th']] = 'd64th'
    

    # Analyze Tracks
    trackbyduration = OrderedDict()
    for trackid in tracks:
        trackbyduration[trackid] = OrderedDict()

        for tick_start in tracks[trackid]['notes']:
            for noteidx in tracks[trackid]['notes'][tick_start]:
                note = tracks[trackid]['notes'][tick_start][noteidx]
                duration = note['tick_duration']

                if duration not in trackbyduration[trackid]:
                    trackbyduration[trackid][duration] = OrderedDict()

                if tick_start not in trackbyduration[trackid][duration]:
                    trackbyduration[trackid][duration][tick_start] = []

                trackbyduration[trackid][duration][tick_start].append(note)

    # Export to Sonic PI
    quater_insecond = (songinfo['tick_time']*songinfo['ntquater']/microseconds)
    vars = "# Converted from midi file with sonic-pi-tools\n"
    vars += "# Github => https://github.com/badele/sonic-pi-tools\n"
    vars += "#\n"
    vars += "# -- MIDI INFO  --\n"
    vars += "# TEMPO (4/4)     = %s µs = %s bpm\n" % (songinfo['tempo'], songinfo['bpm'])
    vars += "# RESOLUTION      = %s\n" % songinfo['resolution']
    vars += "# TICK TIME       = %s µs\n" % songinfo['tick_time']
    vars += "# Quater nb tick  = %s\n" % songinfo['ntquater']
    vars += "# Quater time     = %s s\n" % quater_insecond
    vars += "\n"

    if opts['--played_at_bpm']:
        vars += "dquater=%s\n" % (quater_insecond*(float(opts['--played_at_bpm'])/songinfo['bpm']))
        code = "# Played at %s BPM\n" % opts['--played_at_bpm']
    else:
        vars += "dquater=%s\n" % quater_insecond
        code = "\nuse_bpm %s\n" % songinfo['bpm']

    code += "\n"
    currenttick = OrderedDict([(key,0) for key in trackbyduration[trackid].keys()])

    for trackid in trackbyduration:
        title = tracks[trackid]['title']

        for duration in trackbyduration[trackid]:
            trackfirstnote = trackbyduration[trackid][duration].items()[0][1][0]
            noteduration = duration * songinfo['tick_time']
            pauseduration = (trackfirstnote['tick_start'] - currenttick[duration]) * songinfo['tick_time']

            if noteduration > 0 and noteduration not in uniqtime:
                uniqtime[noteduration] = "d%s" % (len(uniqtime) + 1)

            if pauseduration > 0 and pauseduration not in uniqtime:
                uniqtime[pauseduration] = "d%s" % (len(uniqtime) + 1)

            currenttick[duration] = trackfirstnote['tick_start']
            code += "# %(title)s \n" % locals()
            if pauseduration > 0:
                delay = uniqtime[pauseduration]
                code += "live_loop :track%(trackid)s_d%(duration)s, delay: %(delay)s do\n" % locals()
            else:
                code += "live_loop :track%(trackid)s_d%(duration)s do\n" % locals()

            code += "  with_synth :piano do\n"
            code += "    with_synth_defaults amp: 4 do\n"

            patern_notes = []
            patern_times = []
            for tick_start in trackbyduration[trackid][duration]:
                note = trackbyduration[trackid][duration][tick_start][0]
                noteduration = duration * songinfo['tick_time']
                pauseduration = (note['tick_start'] - currenttick[duration]) * songinfo['tick_time']

                if noteduration > 0 and noteduration not in uniqtime:
                    uniqtime[noteduration] = "d%s" % (len(uniqtime) + 1)

                if pauseduration > 0 and pauseduration not in uniqtime:
                    uniqtime[pauseduration] = "d%s" % (len(uniqtime) + 1)

                nbnotes = len(trackbyduration[trackid][duration][tick_start])
                if nbnotes > 1:
                    # Play chord
                    sleep = ""
                    playnote = ""
                    #trackfirstnote = trackbyduration[trackid][duration][tick_start][0]

                    if len(patern_notes) > 1:
                        tmpnotes = "["
                        tmptimes = "["
                        for idx, value in enumerate(patern_notes):
                            tmpnotes += "%s," % patern_notes[idx]
                            tmptimes += "%s," % patern_times[idx]
                        tmpnotes = "%s]" % tmpnotes[:-1]
                        tmptimes = "%s]" % tmptimes[:-1]
                        code += "      play_pattern_timed %s, %s\n\n" % (tmpnotes, tmptimes)

                        patern_notes = []
                        patern_times = []

                    if pauseduration > 0:
                        sleep += '      sleep %s\n' % uniqtime[pauseduration]

                    pnotes = ""
                    for idx, note in enumerate(trackbyduration[trackid][duration][tick_start]):
                        pnotes += "%s," % note['notename']

                    playnote = "%s      play_chord [%s]\n" % (sleep, pnotes[:-1])
                    playnote += "      sleep %s\n\n" % uniqtime[noteduration]
                    code += playnote

                    currenttick[duration] = note['tick_stop']

                else:
                    # Play pattern
                    if pauseduration > 0:
                        patern_notes.append('nil')
                        patern_times.append(uniqtime[pauseduration])

                    patern_notes.append(note['notename'])
                    patern_times.append(uniqtime[noteduration])
                    currenttick[duration] = note['tick_stop']

            if len(patern_notes) > 1:
                tmpnotes = "["
                tmptimes = "["
                for idx, value in enumerate(patern_notes):
                    tmpnotes += "%s," % patern_notes[idx]
                    tmptimes += "%s," % patern_times[idx]
                tmpnotes = "%s]" % tmpnotes[:-1]
                tmptimes = "%s]" % tmptimes[:-1]
                code += "      play_pattern_timed %s, %s\n\n" % (tmpnotes, tmptimes)
                # else:
                #     firstnote=trackbyduration[trackid][duration][tick_start][0]
                #     currenttick = firstnote['tick_stop']

            code += "      sleep 15\n"

            code += "    end\n"
            code += "  end\n"
            code += "end\n\n"

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

    code = "%s%s" % (vars, code)
    return code


if __name__ == '__main__':
    opts = docopt(__doc__)

    if opts['sonicpi']:
        (songinfo, timelines) = analyseMidiFile(opts['FILE'])
        print convert2SonicPi(songinfo, timelines, opts)