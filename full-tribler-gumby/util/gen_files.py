#!/usr/bin/env python

import os
import sys
from subprocess import check_call

TMPFILE = "tmpfile"

def bs_count_for_size(size):
    """
    Find dd bs and count for given size.
    """
    if size < 128:
        return (None, None)

    # prefer bigger block size
    for bs in (4096*1024, 2048*1024, 1024*1024, 4096, 2048, 1024, 512, 256, 128):
        if size / bs != 0 or size == bs:
            break

    return (bs, size / bs)

def generate_file(size, pattern, tmpfile=TMPFILE):
    try:
        os.unlink(tmpfile + ".mbinmap")
    except OSError:
        pass
    try:
        os.unlink(tmpfile + ".mhash")
    except OSError:
        pass
    # convert to octal escapes for tr
    zeros = "\\000" * len(pattern)
    pattern = "".join(["\\" + "%03d" % int(oct(ord(p))) for p in pattern])

    bs, count = bs_count_for_size(size)
    if bs is None or count is None or size % 4 != 0:
        print >> sys.stderr, "Invalid size. Too small? :)"
        return None

    cmd = "dd if=/dev/zero bs=" + str(bs) + " count=" + str(count) + " | " + \
          "tr '" + zeros + "' '" + pattern + "' > " + tmpfile
    print "Running command:", cmd

    check_call(cmd, shell=True)

def call_swift_for_roothash(tmpfile=TMPFILE):
    # find swift
    if "SWIFTPATH" not in os.environ:
        try:
            TRIBLERPATH = os.environ["TRIBLERPATH"]
            sys.path += [TRIBLERPATH]
        except KeyError:
            print >> sys.stderr, "Please set TRIBLERPATH or SWIFTPATH env var."
            exit(1)
            SWIFTPATH = os.path.join(
                TRIBLERPATH,
                "Tribler",
                "SwiftEngine",
                "swift"
            )
    else:
        SWIFTPATH = os.environ["SWIFTPATH"]

    if not os.path.exists(SWIFTPATH):
        print >> sys.stderr, "Cannot find swift binary."
        exit(1)

    cmd = SWIFTPATH + " -f " + tmpfile + " -m"
    o = check_output(cmd, shell=True)
    return o.split("/")[1][:-1]

if __name__ == "__main__":
    for p in xrange(256):
        # 200MB files, single byte pattern
        size = 1024 * 1024 * 200
        pattern = chr(p)
        generate_file(size, pattern)
        roothash = call_swift_for_roothash()
        print "\"" + str(size) + "-" + pattern.encode("hex") + "\" : \"" + \
              roothash + "\""

    # cleanup
    os.unlink(TMPFILE)
