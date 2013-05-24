#!/usr/bin/env python
#
# usage: PEERLOG="leecher1.log" ./swiftdbg.py > dbg3.html

import os
import operator
from sys import stderr, exit

try:
    PEERLOG = os.environ['PEERLOG']
except KeyError:
    PEERLOG = None

TM = [60 * 60 * 1000000, 60 * 1000000, 1000000, 1000, 1]

def parse_timestamp(t):
    try:
        return reduce(
            operator.add,
            map(operator.mul, TM, [int(x) for x in t.split('_')]),
            0
        )
    except:
        return None

def parse_bin_std_form(bin):
    [layer, layer_offset] = bin[1:-1].split(',')
    interval = [
        int(layer_offset) * pow(2, int(layer)),             # start chunk
        ((int(layer_offset) + 1) * pow(2, int(layer))) - 1  # end chunk
    ]
    return interval

data = ['_'] * 98304

def event_recv_have(start, end):
    # do something then return log message
    return 'event_recv_have: ' + str(start) + ' ' + str(end)

def event_recv_hash(start, end):
    # do something then return log message
    for i in range(start, end + 1):
        if data[i] != 'D' and data[i] != 'A':
            # if data is not already received
            data[i] = 'H'
    return 'event_recv_hash: ' + str(start) + ' ' + str(end)

def event_recv_data(start, end):
    # do something then return log message
    for i in range(start, end + 1):
        if data[i] != 'A':
            # if not already acked
            data[i] = 'D'
    return 'event_recv_data: ' + str(start) + ' ' + str(end)

def event_recv_data_bad(start, end):
    # do something then return log message
    return 'event_recv_data_bad: ' + str(start) + ' ' + str(end)

def event_send_ack(start, end):
    # do something then return log message
    for i in range(start, end + 1):
        data[i] = 'A'
    return 'event_recv_data_bad: ' + str(start) + ' ' + str(end)

def add_event(func, time, args):
    l = func(*args)
    #print time, l

if __name__ == "__main__":
    if PEERLOG is None:
        print >>stderr, 'Please set PEERLOG env var.'
        exit(1)

    peerlog = open(PEERLOG, 'r')

    for line in peerlog.readlines():
        l = [x.strip() for x in line.split(' ')]
        timestamp = parse_timestamp(l[0])
        try:
            if l[2] == '-have':
                add_event(event_recv_have, time=timestamp, args=parse_bin_std_form(l[3]))
            if l[2] == '-hash':
                add_event(event_recv_hash, time=timestamp, args=parse_bin_std_form(l[3]))
            if l[2] == '-data':
                add_event(event_recv_data, time=timestamp, args=parse_bin_std_form(l[3]))
            if l[2] == '!data':
                add_event(event_recv_data_bad, time=timestamp, args=parse_bin_std_form(l[3]))
            if l[2] == '+ack':
                add_event(event_send_ack, time=timestamp, args=parse_bin_std_form(l[3]))
        except IndexError:
            pass

    peerlog.close()

    print """<script>
    var s = "{data}";
    function test() {{
        var example = document.getElementById('example');
        var context = example.getContext('2d');

        var x = 0;
        var y = 0;
        for (var i = 0; i < s.length; i++) {{
            if (s.charAt(i) == '_') {{
                context.fillStyle = 'grey';
            }} else if (s.charAt(i) == 'D') {{
                context.fillStyle = 'green';
            }} else if (s.charAt(i) == 'H') {{
                context.fillStyle = 'blue';
            }} else if (s.charAt(i) == 'A') {{
                context.fillStyle = '#98fb98';
            }}
            context.fillRect(x, y, 5, 5);
            x = x + 5;
            if (x > 1200) {{
                x = 0;
                y = y + 5;
            }}
        }}
    }}
    </script>""".format(data=''.join(data).strip())

    print '<style>'
    print 'span { display: inline-block; float: left; }'
    print '.greenbox { width: 5px; height: 5px; background-color: green; }'
    print '.redbox { width: 5px; height: 5px; background-color: red; }'
    print '</style>'

    print '<body onload="test()">'
    print '<p>grey = nothing received for this chunk</p>'
    print '<p>blue = hash received</p>'
    print '<p>green = data received</p>'
    print '<p>light green = ack sent</p>'
    print '''<canvas id="example" width="1200" height="5000">
    This text is displayed if your browser does not support HTML5 Canvas.
    </canvas>'''
    print '</body>'