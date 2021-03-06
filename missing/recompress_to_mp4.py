#!/usr/bin/env python

from __future__ import division
from __future__ import print_function

import argparse
import glob
import os
import time
from itertools import chain

parser = argparse.ArgumentParser()
parser.add_argument('--bitrate', '-b', help='specify output bitrate for video')
parser.add_argument('--converter', help='Manually specify [full path to] ffmpeg or avconv')
parser.add_argument('--copy', '-C', action='store_true', help='No-op copy, e.g. for cutting or remuxing')
parser.add_argument('--copy-audio', '-c', action='store_true')
parser.add_argument('--deinterlace', '-d', action='store_true', help='deinterlace with yadif (requires recoding)')
parser.add_argument('--duration', '-t', help='Duration limit for encoding')
parser.add_argument('--framerate', '-r', help='specify output FPS for video')
parser.add_argument('--hwaccel', '-hw', help='specify input hardware acceleration')
parser.add_argument('--nv', '-nv', action='store_true', help='Enable both nvdec and nvenc for transcoding')
parser.add_argument('--nvdec', '-nvd', action='store_true')
parser.add_argument('--nvenc', '-nve', action='store_true')
parser.add_argument('--quality', '-q', type=int, default=23)
parser.add_argument('--stabilize', '-stab', action='store_true')
parser.add_argument('--start', '-ss', type=float, help='Start time for encoding in seconds')
parser.add_argument('files_or_globs', nargs='+')


def makedirs(path, exist_ok=True):
    # Py 2.7 planned obsolescence (not including trivial feature improvements)
    if exist_ok and os.path.exists(path):
        return
    os.makedirs(path)


def duration_format(duration):
    """Format a float of seconds as number and H:M:S string.

    For example:
    >>> duration_format(123)
    '123.00 s (00:02:03)'

    >>> duration_format(12345.67)
    '12345.67 s (03:25:45)'
    """
    duration_tuple = time.gmtime(duration)
    return '{:.2f} s ({})'.format(float(duration), time.strftime('%H:%M:%S', duration_tuple))


def time_format(timestamp):
    time_tuple = time.gmtime(timestamp)
    return time.strftime('%H:%M:%S', time_tuple)


class TimedSystem:
    def __init__(self):
        self.total = 0
        self.log = []

    def run(self, command):
        start = time.time()
        print(time.strftime('%H:%M:%S'), 'starting', command)
        status = os.system(command)
        finish = time.time()
        elapsed = finish - start
        print(time.strftime('%H:%M:%S'), 'finished in: ', duration_format(elapsed))
        self.total += elapsed
        self.log.append((command, start, finish, elapsed))
        if status != 0:
            raise RuntimeError('Error (status={}) executing command: {}'.format(status, command))
        return status

    def report(self):
        for command, start, finish, elapsed in self.log:
            print(time_format(start), command)
            print(time_format(finish), 'took:', duration_format(elapsed))
        print(time.strftime('%H:%M:%S'), 'Finished in: ', duration_format(self.total))


def ratio_format(pre, post):
    return '{:,}\t{:,}\t{:.1f}%\t{:.1f}x\t{:,}'.format(pre, post, 100*post/pre, pre/post, post-pre)


class CompressionStats:
    def __init__(self):
        self.items = []
        self.total_pre = 0
        self.total_post = 0

    def add(self, before, after):
        size_pre = os.path.getsize(before)
        size_post = os.path.getsize(after)
        if size_post == 0:
            raise ValueError('Empty output file: {}'.format(after))
        self.total_pre += size_pre
        self.total_post += size_post
        self.items.append((os.path.basename(before), size_pre, size_post))
        return size_pre / size_post

    def report(self):
        for name, before, after in self.items:
            print('{}\t{}'.format(name, ratio_format(before, after)))
        print('Total:\t{}'.format(ratio_format(self.total_pre, self.total_post)))


try:
    from shutil import which
except ImportError:
    def which(program):
        # https://stackoverflow.com/a/377028/1338797
        import os

        def is_exe(file_path):
            return os.path.isfile(file_path) and os.access(file_path, os.X_OK)

        fpath, fname = os.path.split(program)
        if fpath:
            if is_exe(program):
                return program
        else:
            for path in os.environ["PATH"].split(os.pathsep):
                path = path.strip('"')
                exe_file = os.path.join(path, program)
                if is_exe(exe_file):
                    return exe_file

        return None


if __name__ == '__main__':
    args = parser.parse_args()

    input_options = ''
    if args.nv or args.nvdec:
        input_options += '-hwaccel nvdec'
    if args.hwaccel:
        input_options += '-hwaccel {}'.format(args.hwaccel)

    common_options = ' -map_metadata 0 -pix_fmt yuv420p  -strict -2'

    if args.deinterlace:
        common_options += ' -vf yadif'

    if args.nv or args.nvenc:
        encoder_options = 'h264_nvenc -cq {} -preset slow {}'.format(args.quality, common_options)
        # this looks promising, but for now produces overkill
        # https://superuser.com/a/1236387/269542
        # encoder_options = ('h264_nvenc -preset llhq -rc:v vbr_minqp -qmin:v 19 -qmax:v 21 -b:v 2500k '
        #                    '-maxrate:v 5000k -profile:v high ' + common_options)
    else:
        encoder_options = 'h264 -crf {} -preset veryslow {}'.format(args.quality, common_options)

    if args.bitrate:
        encoder_options += ' -b:v {}'.format(args.bitrate)

    if args.framerate:
        encoder_options += ' -r {}'.format(args.framerate)

    if args.duration:
        encoder_options += ' -t {}'.format(args.duration)

    makedirs('original', exist_ok=True)
    makedirs('converted', exist_ok=True)

    converter = args.converter
    if converter is None:
        converter = which('ffmpeg')
    if converter is None:
        converter = which('avconv')
    if converter is None:
        print('Neither ffmpeg nor avconv found.')
        exit()

    print('Using:', converter)

    ts = TimedSystem()
    stats = CompressionStats()

    for filename in chain.from_iterable(map(glob.glob, args.files_or_globs)):
        basename = os.path.basename(filename)
        original = os.path.join('original', basename)
        os.rename(filename, original)
        converted = os.path.splitext(os.path.join('converted', basename))[0] + '.mp4'
        filters = ''
        if args.stabilize:
            preprocessing = '{} -i "{}" -vf vidstabdetect -f null -'.format(
                converter,
                original
            )
            ts.run(preprocessing)
            filters += ' -vf vidstabtransform,unsharp=5:5:0.8:3:3:0.4'

        if args.start:
            filters += ' -ss {:.2f}'.format(args.start)

        commandline = '{} {} -i "{}" {} -c:a {} -c:v {} "{}"'.format(
            converter,
            input_options,
            original,
            filters,
            'copy' if args.copy_audio or args.copy else 'aac',
            'copy' if args.copy else encoder_options,
            converted)
        ts.run(commandline)

        ratio = stats.add(original, converted)

        if ratio < 1.25:
            dump_dir = 'placebo' if ratio > 1 else 'nocebo'
            print(basename, 'compressed {:.1f}x'.format(ratio), 'which is', dump_dir)
            makedirs(dump_dir, exist_ok=True)
            os.rename(converted, os.path.join(dump_dir, os.path.basename(converted)))

    ts.report()
    stats.report()
