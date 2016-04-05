# (c) Copyright 2014 Synapse Wireless, Inc.
"""
EchoTest.py - a simple benchmark used to determine how fast SNAP Connect can
communicate with a directly connected bridge. We use this to evaluate different
Python platforms, implementations, and serial drivers.

This example demonstrates one way to maximize throughput without choking the network.

Refer to comments throughout this file, plus the accompanying README.txt.
"""

import logging
from snapconnect import snap
import time


# NOTE: Ensure that the Feature bits setting on this device has both (0x100) second data CRC
#       and (0x400) packet CRC disabled
BRIDGE_NODE = "\x4B\x42\x34" # <- Replace this with the address of your bridge node

# Note the hardcoded COM1 usage.
# You should set these to match YOUR available hardware
SERIAL_TYPE = snap.SERIAL_TYPE_RS232
#SERIAL_TYPE = snap.SERIAL_TYPE_SNAPSTICK100
#SERIAL_TYPE = snap.SERIAL_TYPE_SNAPSTICK200

# If you're on a unix platform, you'll need to specify the interface type differently than windows
# An example for a typical interface device is shown below
SERIAL_PORT = 0 # COM1
#SERIAL_PORT = '/dev/ttyS1'

NUMBER_OF_QUERIES = 100 # More polls == longer test
TIMEOUT = 1.0 # (in seconds) You might need to increase this if:
# 1) You change the RPC call being made
# If you are invoking some custom function of your own, and it takes longer for the
# nodes to respond - for example, some function that performs multiple analog readings
# and then computes a result.
# 2) You are benchmarking a remote node, and it is so many hops away that 1 second is too short.

# You could experiment with various size payloads.
# Note that PAYLOAD is just one of several parameters to the actual RPC call
#PAYLOAD = "A"
#PAYLOAD = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
#PAYLOAD = "ABCDEFGHIJKLMNOPQRSTUVWXYZABCDEFGHIJKLMNOPQRSTUVWXYZABCDEFGHIJKLMNOP"
PAYLOAD = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890-=<({[]})=-!@#$" # this is the biggest payload that will fit (RPC_CRC == OFF, PACKET_CRC == OFF)
# The only way to get a bigger payload would be to shorten the callback function's name (currently "response_handler")
# Also note that if you were to turn *ON* the RPC_CRC feature, that would also use up
# two bytes of each packet, requiring the PAYLOAD string to be shortened by two bytes to compensate.

# Initialize global variables
test_complete = False
test_started = False
polls_sent = 0
replies = 0
sent_id = None

def initiate_test(repeats):
    """Kick off a test run"""
    global poll_limit, start_time, test_started
    test_started = True
    poll_limit = repeats
    start_time = time.time()
    send_next_poll()
    print 'Initiating test sequence'

def show_results():
    """Display some simple statistics about the test run"""
    end_time = time.time()
    delta = end_time - start_time
    delta *= 1000 # so we can show it in integer milliseconds
    print "%d queries, %d responses in %d milliseconds" % (polls_sent, replies, delta)

def send_next_poll():
    """Send the next poll (RPC) if there are any remaining, else flag the test as complete"""
    global test_complete, sent_id
    if polls_sent < poll_limit:
        #
        # Notice that here we are only invoking built-in SNAPpy functions, to eliminate
        # the need to put a SNAPpy script on the node.
        #

        # Notice that here we are sending the PAYLOAD "round-trip"
        sent_id = comm.rpc(BRIDGE_NODE, 'callback', 'response_handler', 'str', PAYLOAD)
        # If you only wanted to send the payload TO the node, you could do
        #comm.rpc(BRIDGE_NODE, 'callback', 'response_handler', 'len', PAYLOAD)
        # If you didn't want to send the PAYLOAD at all you could do something like
        #comm.rpc(BRIDGE_NODE, 'callback', 'response_handler', 'random')
    else:
        test_complete = True

def response_handler(value):
    """Handler incoming replies to our poll RPCs"""
    global replies, timeoutEvent

    timeoutEvent.Stop() # Cancel the timeout, we DID get a reply

    replies += 1
    send_next_poll()
    print 'received %d replies\r'%replies,

def timeout_handler():
    """Handler LACK OF incoming replies to our poll RPCs"""
    send_next_poll()

def rpc_sent_handler(packet_id, future_use):
    """Handle handoff of each packet"""
    global polls_sent, timeoutEvent

    if sent_id == packet_id:
        polls_sent += 1
        timeoutEvent = comm.scheduler.schedule(TIMEOUT, timeout_handler)

def serial_open_handler(serial_type, serial_port, addr):
    # Initiate the test after we know our serial port is opened
    initiate_test(NUMBER_OF_QUERIES)

def main():
    """Simple benchmark. Create a SNAP Connect instance, and use it to send a batch of RPC calls"""
    global comm

    # Create a SNAP Connect object to do communications (comm) for us
    comm = snap.Snap(funcs = {})

    comm.add_rpc_func('response_handler', response_handler)

    # By tieing into HOOK_RPC_SENT events, we can avoid needlessly "piling up" RPC calls INSIDE THIS PC
    comm.set_hook(snap.hooks.HOOK_RPC_SENT, rpc_sent_handler)

    # By tieing into the HOOK_SERIAL_OPEN event, we can wait until we know we have a connected device to start the test
    comm.set_hook(snap.hooks.HOOK_SERIAL_OPEN, serial_open_handler)
    comm.open_serial(SERIAL_TYPE, SERIAL_PORT)

    # Wait for all the queries to be sent, and all the replies to be received (or timed out)
    while not test_complete:
        comm.poll()

    show_results()

if __name__ == "__main__":
    # Notice that because this is a benchmark, we have set logging to the LEAST verbose level
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    main()

