
import cocotb
from cocotb.triggers import Timer

from fifo_helpers import (
    start_clocks,
    reset_fifo,
    write_fifo,
    read_fifo,
)
from fifo_scoreboard import FIFOScoreboard
from fifo_monitors import monitor_writes, monitor_reads


@cocotb.test()
async def test_scoreboard_integration(dut):
    start_clocks(dut)
    await reset_fifo(dut)

    scoreboard = FIFOScoreboard()

    write_monitor = cocotb.start_soon(
        monitor_writes(dut, scoreboard)
    )
    read_monitor = cocotb.start_soon(
        monitor_reads(dut, scoreboard)
    )

    test_data = [0xA5, 0x3C, 0xF0, 0x12]

    for value in test_data:
        await write_fifo(dut, value)

    for _ in test_data:
        await read_fifo(dut)

    # Allow monitor tasks to complete their edge processing.
    await Timer(2, unit="ns")

    scoreboard.evaluate()

    assert scoreboard.writes == 4, (
        f"Expected 4 writes, got {scoreboard.writes}"
    )

    assert scoreboard.reads == 4, (
        f"Expected 4 reads, got {scoreboard.reads}"
    )

    scoreboard.assert_no_errors()

    scoreboard.check_empty()

    write_monitor.cancel()
    read_monitor.cancel()
