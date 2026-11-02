
import random

import cocotb
from cocotb.triggers import FallingEdge, RisingEdge, Timer

from fifo_helpers import start_clocks, reset_fifo
from fifo_monitors import monitor_writes, monitor_reads
from fifo_scoreboard import FIFOScoreboard


@cocotb.test()
async def test_fifo_random(dut):
    seed = 20261101
    rng_write = random.Random(seed)
    rng_read = random.Random(seed + 1)

    start_clocks(dut, wperiod=10, rperiod=14)
    await reset_fifo(dut)

    scoreboard = FIFOScoreboard()

    write_monitor = cocotb.start_soon(
        monitor_writes(dut, scoreboard)
    )
    read_monitor = cocotb.start_soon(
        monitor_reads(dut, scoreboard)
    )

    # Run independent random traffic generators.
    async def writer():
        for _ in range(500):
            await FallingEdge(dut.wclk)

            dut.winc.value = int(
                rng_write.random() < 0.75
            )
            dut.wdata.value = rng_write.randrange(256)

        await FallingEdge(dut.wclk)
        dut.winc.value = 0

    async def reader():
        for _ in range(500):
            await FallingEdge(dut.rclk)

            dut.rinc.value = int(
                rng_read.random() < 0.75
            )

        await FallingEdge(dut.rclk)
        dut.rinc.value = 0

    writer_task = cocotb.start_soon(writer())
    reader_task = cocotb.start_soon(reader())

    await writer_task
    await reader_task

    # Drain remaining FIFO contents.
    for _ in range(100):
        await FallingEdge(dut.rclk)

        if int(dut.rempty.value) == 0:
            dut.rinc.value = 1
        else:
            dut.rinc.value = 0

        await RisingEdge(dut.rclk)
        await Timer(1, unit="ns")

    dut.rinc.value = 0

    await Timer(20, unit="ns")

    write_monitor.cancel()
    read_monitor.cancel()

    scoreboard.evaluate()

    scoreboard.assert_no_errors()
    scoreboard.check_empty()

    assert scoreboard.writes > 0
    assert scoreboard.reads > 0

    dut._log.info(
        f"Random test seed={seed}, "
        f"writes={scoreboard.writes}, "
        f"reads={scoreboard.reads}"
    )
