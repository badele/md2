# coding: utf-8

"""Usage: midi2md2.py [--title=<title>] [--verbose] [--played_at_bpm=<bpm>] FILE
       midi2md2.py text FILE

Convert FILE to other format

Arguments:
    FILE            Midi filename

Options:
    -h, --help      Help

"""

from docopt import docopt

import mididecode

import os

def getSpeedText(tick_ref,tick_value):
    """
    Return Note text speed from tick speed reference
    :param tick_ref:
    :param tick_value:
    :return:
    """
    slow = "⏪"
    fast = "⏩"

    if tick_ref == tick_value:
        return ""

    speed = tick_value / float(tick_ref)
    if speed < 1:
        ratio = 1.0 / speed
        direction = fast
        symbol = ('%f' % ratio).rstrip('0').rstrip('.')
    else:
        direction = slow
        symbol = ('%f' % speed).rstrip('0').rstrip('.')

    return "%s%s" % (direction,symbol)


def songinfo(songinfo, opts):
    """
    Return md2 format song
    :param songinfo:
    :param opts:
    :return:
    """
    microseconds = 1000000.0
    filename = os.path.basename(opts['FILE'])
    title = filename
    if opts['--title']:
        title = opts['--title']

    print "# %(title)s\n" % locals()
    print "## Summary\n"

    si = songinfo['songinfo']
    summary = "* file = %s\n" % filename
    summary += "* version = 1.0\n"
    summary += "* %s = %s bpm (%s s)" % (
        si['note_unit'],
        ("%.2f" % si['bpm']).rstrip('0').rstrip('.'),
        si['tempo'] / microseconds
    )

    if opts['--verbose']:
        summary += "Tempo (%s/%s)        = %s µs (%.4f s) = %s bpm\n" % (
            si['numerator'],
            si['denominator'],
            si['tempo'],
            si['tempo'] / microseconds,
            si['bpm']
        )
        summary += "Measure resolution = %s ticks (%s s)\n" % (si['resolution'], si['resolution'] * si['tick_time'] / microseconds)
        summary += "Note Duration      = %s / %s ticks (%s s)\n" % (si['note_unit'],si['note_tick'], si['note_tick'] * si['tick_time'] / microseconds)
        summary += "Song Duration      = %s second" % (si['tick_time']/microseconds * si['stop'])
        summary += "Resolution      = %s ticks\n" % si['resolution']
        summary += "Ticks time      = %s µs (%.4f s)\n" % (si['tick_time'],si['tick_time']/microseconds)

    print summary

    print "\n## Tracks"

    for trackid in songinfo['tracks']:
        track = songinfo['tracks'][trackid]
        tracktitle = track['trackinfo']['title']

        print "\n### %(tracktitle)s\n" % locals()

        tn = track['notes']
        previoustick = 0
        lines = ""
        for absticks in tn:
            pauseline = ""
            if absticks != previoustick:
                pause = absticks - previoustick

                pauseline += "P%s" % getSpeedText(si['note_tick'], pause)


            maxduration = 0
            for tduration, value in tn[absticks].items():
                if tduration > maxduration:
                    maxduration = tduration
                noteline = ""
                for nodeidx, noteinfo in tn[absticks][tduration].items():
                    noteline += "%s%s " % (
                        noteinfo['notename'],
                        noteinfo['octave'],
                    )
                noteline = noteline.strip()

                if len(tn[absticks][tduration]) > 1:
                    noteline = '(%s)' % noteline

                noteline += "%s" % getSpeedText(si['note_tick'], tduration)

            previoustick = absticks + maxduration

            if pauseline != "":
                lines += "\n%s " % pauseline

            lines += "%s " % noteline

        lines = lines.strip()
        print "```\n%(lines)s\n```" % locals()


if __name__ == '__main__':
    opts = docopt(__doc__)

    minfo = mididecode.analyseMidiFile(opts['FILE'])
    sinfo = songinfo(minfo, opts)