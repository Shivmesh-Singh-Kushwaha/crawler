#!/usr/bin/env python3
import time
import functools
from threading import Thread
from itertools import count
import asyncio
import queue

import janus


class Timer():
    def __init__(self):
        self._start = None

    def start(self):
        self._start = time.time()

    def stop(self):
        return time.time() - self._start


def consumer_thread_sync(taskq, result):
    while True:
        task = taskq.get()
        if task is None:
            return
        result[0] = task


async def consumer_thread_async(taskq, result):
    while True:
        task = await taskq.get()
        if task is None:
            return
        result[0] = task


async def producer_thread_async(taskq):
    for x in range(10000 + 1):
        await taskq.put(x)
    await taskq.put(None)


def producer_thread_sync(taskq):
    for x in range(10000 + 1):
        taskq.put(x)
    taskq.put(None)


def bench_sync_async():
    taskq = janus.Queue(maxsize=100)

    loop = asyncio.get_event_loop()

    result = [None]
    consumer = Thread(target=consumer_thread_sync, args=[taskq.sync_q, result])
    consumer.start()

    loop.run_until_complete(producer_thread_async(taskq.async_q))
    consumer.join()

    taskq.close()
    loop.run_until_complete(taskq.wait_closed())

    assert result[0] == 10000


def bench_async():
    taskq = asyncio.Queue(maxsize=100)

    loop = asyncio.get_event_loop()

    result = [None]
    consumer = loop.create_task(consumer_thread_async(taskq, result))
    loop.create_task(producer_thread_async(taskq))
    loop.run_until_complete(consumer)

    assert result[0] == 10000


def bench_sync():
    taskq = queue.Queue(maxsize=100)

    loop = asyncio.get_event_loop()

    result = [None]
    consumer = Thread(target=consumer_thread_sync, args=[taskq, result])
    consumer.start()

    producer = Thread(target=producer_thread_sync, args=[taskq])
    producer.start()

    consumer.join()

    assert result[0] == 10000


def main(**kwargs):
    timer = Timer()

    timer.start()
    bench_sync_async()
    elapsed1 = timer.stop()

    #timer.start()
    #bench_async()
    #elapsed2 = timer.stop()

    #timer.start()
    #bench_sync()
    #elapsed3 = timer.stop()

    print('------------------------------------')
    print('Sync + async: %.2f sec.' % elapsed1)
    #print('Async: %.2f sec.' % elapsed2)
    #print('Sync: %.2f sec.' % elapsed3)



if __name__ == '__main__':
    main()
