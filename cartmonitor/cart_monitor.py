#!/usr/bin/env python3
"""
Dynamic analyser of a cart controller.
"""
from email import contentmanager
from jarvisenv import Jarvis 
import itertools

slots = 4
w_capacity = 150
stations = Jarvis.get_tracks().stations()
cart_slots = [() for i in range(slots)]
requests = []
global err_val
err_val = False

def gen_empty(stations, slots):
    lst = {}
    arr = [False for i in range(slots)]
    for station in stations:
        lst.update({station: arr[:]})
    return lst


# covered = {"A": [True, True, False, True], "B": [True, False, False, True]}
covered = gen_empty(stations, slots)

def set_covered(station, slot_num):
    arr = covered[station]
    arr[slot_num] = True
    covered.update({station: arr})

def report_coverage():
    "Coverage reporter"
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # Zde nahradte vypocet/vypis aktualne dosazeneho pokryti
    curr_cov = 0
    curr_cov = list(itertools.chain.from_iterable(covered.values())).count(True)

    stations_count = len(stations)
    cov = (curr_cov / (slots * stations_count)) * 100

    print('CartCoverage %d%%' % cov)

def onmoving(time, pos1, pos2):
    global err_val
    "priklad event-handleru pro udalost moving"
    for tpl in cart_slots:
        if(tpl != ()):
            _, pos, content, _ = tpl
            if(pos == pos1):
                print("%d:error: content: \"%s\" was not unloaded in station: \"%s\"" % (int(time), content, pos))
                err_val = True

def onloading(time, pos, content, weight, slot):
    global err_val
    if(int(slot) >= slots):
        print("%d:error: loading over cart slot capacity." % int(time))
        err_val = True
    else:
        set_covered(pos, int(slot))
        if(len(cart_slots) != 0 and cart_slots[int(slot)] != ()):
            print("%d:error: loading into an occupied slot #%d" % (int(time), int(slot)))
            err_val = True
        found = False
        for pos1, pos2, content_r, weight_r in requests:
            if(pos1 == pos and content == content_r and weight == weight_r):
                found = True
                w_counter = 0
                for sl in cart_slots:
                    if(sl != ()):
                        _, _, _, w = sl
                        w_counter += int(w)
                if(w_counter + int(weight_r) > w_capacity):
                    print("%d:error: loading content: \"%s\" over cart weight capacity: \"%d\"" % (int(time), content, w_capacity))
                    err_val = True
                cart_slots[int(slot)] = (pos1, pos2, content_r, weight_r)
        if(found == False):
            print("%d:error: loading content: \"%s\" without request in station: \"%s\"" % (int(time), content, pos))
            err_val = True
        
def onunloading(time, pos, content, weight, slot):
    global err_val
    if(len(cart_slots) != 0 and cart_slots[int(slot)] == ()):
        print("%d:error: unloading from an unoccupied slot #%d" % (int(time), int(slot)))
        err_val = True
    for pos1, pos2, content_r, weight_r in requests:
        if(pos == pos1 and content == content_r and weight == weight_r):
            requests.remove((pos, pos2, content, weight))
            
    cart_slots[int(slot)] = ()

def onrequesting(time, pos1, pos2, content, weight):
    requests.append((pos1, pos2, content, weight))

def onevent(event):
    "Event handler. event = [TIME, EVENT_ID, ...]"
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # ZDE IMPLEMENTUJTE MONITORY
    # print(event)

    # vyjmeme identifikaci udalosti z dane n-tice
    event_id = event[1]
    del(event[1])
    # priklad predani ke zpracovani udalosti moving
    if event_id == 'moving':
        onmoving(*event)
    elif event_id == "loading":
        onloading(*event)
    elif event_id == "unloading":
        onunloading(*event)
    elif event_id == "requesting":
        onrequesting(*event)
    elif event_id == "stop":
        if(err_val == False):
            print("All properties hold.")

###########################################################
# Nize netreba menit.

def monitor(reader):
    "Main function"
    for line in reader:
        line = line.strip()
        onevent(line.split())
    report_coverage()

if __name__ == "__main__":
    import sys
    monitor(sys.stdin)
