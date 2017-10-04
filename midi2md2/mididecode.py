# coding: utf-8

from collections import OrderedDict

import midi

notes_list = OrderedDict({
    'dwhole': 2,
    'whole': 1,
    'minim': 1/2.0,
    'quater': 1/4.0,
    'eighth': 1/8.0,
    'sixteenth': 1/16.0,
    '32th': 1/32.0,
    '64th': 1/64.0
})

def analyseMidiFile(filename):

    notes = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

    mi = {'songinfo': {'nbtracks': 0}, 'tracks':OrderedDict()}

    pattern = midi.read_midifile(filename)

    # Search BPM
    mi['songinfo']['resolution'] = pattern.resolution
    mi['songinfo']['noteduration'] = OrderedDict()

    # Get MIDI information from track #0
    for pinfo in pattern[0]:
        if type(pinfo) == midi.TimeSignatureEvent:
            mi['songinfo']['numerator'] = pinfo.data[0]
            mi['songinfo']['denominator'] = 2 ** pinfo.data[1]


            mi['songinfo']['note_index'] = mi['songinfo']['denominator'] - 1
            mi['songinfo']['note_unit'] = sorted(notes_list.items(), key=lambda t: t[1],reverse=True)[mi['songinfo']['note_index']][0]
            mi['songinfo']['note_duration'] = sorted(notes_list.items(), key=lambda t: t[1],reverse=True)[mi['songinfo']['note_index']][1]
            mi['songinfo']['note_tick'] = mi['songinfo']['resolution'] / mi['songinfo']['numerator']

            mi['songinfo']['tick_per_metronome'] = pinfo.data[2]
            mi['songinfo']['ppqn'] = mi['songinfo']['resolution'] / mi['songinfo']['numerator']

            # If not 4/4 partition, raise exception
            if mi['songinfo']['numerator'] != 4 and mi['songinfo']['denominator'] != 4:
                raise Exception("Cannot convert this midi file (numerator/denominator) compatibility")

        if type(pinfo) == midi.SetTempoEvent:
            tempo = pinfo.data[0] * 256**2 + pinfo.data[1] * 256 + pinfo.data[2]
            mi['songinfo']['tempo'] = tempo
            mi['songinfo']['bpm'] = 60000000 / float(tempo)
            mi['songinfo']['tick_time'] = tempo / float(mi['songinfo']['resolution']) * mi['songinfo']['bpm']/60.0

    # Parse track
    minticks = 99999999
    maxticks = 0
    minduration = 99999999
    maxduration = 0
    for trackid, track in enumerate(pattern):
        if trackid == 0:
            continue

        absticks = 0
        currentinfos = OrderedDict()
        mi['tracks'][trackid] = {'notes': OrderedDict(), 'trackinfo': {'title': '', 'noteduration': {}}}

        eventidx = 0
        nbnotes = 0
        for event in pattern[trackid]:
            if type(event) == midi.TrackNameEvent:
                mi['tracks'][trackid]['trackinfo'] = {
                    'title': event.text,
                    'tick_start': 99999999,
                    'tick_stop': -1,
                    'noteduration': {}
                }

            if type(event) == midi.events.NoteOnEvent or type(event) == midi.events.NoteOffEvent:
                noteidx = event.data[0]
                noteinoct = event.data[0] % 12
                notename = notes[noteinoct]
                octave = event.data[0]/12
                absticks += event.tick


                if type(event) == midi.events.NoteOnEvent:

                    if absticks < minticks:
                        minticks = absticks

                    # Store first tick note
                    if absticks < mi['tracks'][trackid]['trackinfo']['tick_start']:
                        mi['tracks'][trackid]['trackinfo']['tick_start'] = absticks

                    # Add note
                    noteinfo = {}
                    nbnotes += 1
                    eventidx += 1
                    noteinfo['eventidx'] = eventidx
                    noteinfo['noteidx'] = noteidx
                    noteinfo['octave'] = octave
                    noteinfo['notename'] = notename
                    noteinfo['tick_start'] = absticks
                    noteinfo['tick_stop'] = -1

                    if absticks not in mi['tracks'][trackid]['notes']:
                        mi['tracks'][trackid]['notes'][absticks] = OrderedDict()

                    # Add starting note
                    if noteidx not in currentinfos:
                        currentinfos[noteidx] = []
                    currentinfos[noteidx].append(noteinfo)


                if type(event) == midi.events.NoteOffEvent:
                    # Store last tick note for the track
                    if absticks > mi['tracks'][trackid]['trackinfo']['tick_stop']:
                        mi['tracks'][trackid]['trackinfo']['tick_stop'] = absticks

                    # Store max tick note for all track
                    if absticks > maxticks:
                        maxticks = absticks

                    noteinfo = currentinfos[noteidx].pop(0)
                    tickpos = noteinfo['tick_start']

                    noteinfo['tick_stop'] = absticks
                    duration = noteinfo['tick_stop'] - noteinfo['tick_start']

                    noteinfo['tick_duration'] = duration

                    if duration not in mi['tracks'][trackid]['notes'][tickpos]:
                        mi['tracks'][trackid]['notes'][tickpos][duration] = OrderedDict({noteidx: OrderedDict()})
                    mi['tracks'][trackid]['notes'][tickpos][duration][noteidx] = noteinfo

                    # Count song duration
                    if duration not in mi['songinfo']['noteduration']:
                        mi['songinfo']['noteduration'][duration] = 0
                    mi['songinfo']['noteduration'][duration] += 1

                    # Count track duration
                    if duration not in mi['tracks'][trackid]['trackinfo']['noteduration']:
                        mi['tracks'][trackid]['trackinfo']['noteduration'][duration] = 0
                    mi['tracks'][trackid]['trackinfo']['noteduration'][duration] += 1

                    if duration > maxduration:
                        maxduration = duration

                    if duration < minduration:
                        minduration = duration

                mi['tracks'][trackid]['trackinfo']['nbnotes'] = nbnotes

        mi['songinfo']['start'] = minticks
        mi['songinfo']['stop'] = maxticks
        mi['songinfo']['minduration'] = minduration
        mi['songinfo']['maxduration'] = maxduration

    # Delete track with no datas
    for _,trackid in enumerate(mi['tracks']):
        if 'nbnotes' not in mi['tracks'][trackid]['trackinfo']:
            del mi['tracks'][trackid]
    mi['songinfo']['nbtracks'] = len(mi['tracks'])

    return mi