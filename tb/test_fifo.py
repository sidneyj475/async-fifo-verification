
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import FallingEdge, RisingEdge, Timer
from fifo_helpers import (
    start_clocks,
    reset_fifo,
    write_fifo,
    read_fifo,
)

@cocotb.test()
async def test_fifo_basic(dut):
    # Initialize inputs
    dut.winc.value = 0
    dut.rinc.value = 0
    dut.wdata.value = 0
    dut.wrst_n.value = 0
    dut.rrst_n.value = 0

    # Start independent clocks
    cocotb.start_soon(Clock(dut.wclk, 10, unit="ns").start())
    cocotb.start_soon(Clock(dut.rclk, 14, unit="ns").start())

    # Hold reset for several clock cycles
    await Timer(50, unit="ns")

    assert int(dut.rempty.value) == 1, "FIFO should be empty after reset"
    assert int(dut.wfull.value) == 0, "FIFO should not be full after reset"

    # Release reset
    dut.wrst_n.value = 1
    dut.rrst_n.value = 1

    await Timer(50, unit="ns")

    # Write one byte, keeping inputs stable across one write edge
    await RisingEdge(dut.wclk)
    await Timer(1, unit="ns")
    dut.wdata.value = 0xA5
    dut.winc.value = 1

    await RisingEdge(dut.wclk)
    await Timer(1, unit="ns")
    dut.winc.value = 0

    # Wait for write pointer synchronization into read domain
    for _ in range(10):
        await RisingEdge(dut.rclk)
        await Timer(1, unit="ns")
        if int(dut.rempty.value) == 0:
            break
    else:
        assert False, "FIFO never became non-empty"

    # Asynchronous memory output should show oldest data
    assert int(dut.rdata.value) == 0xA5, "Incorrect FIFO data"

    # Read one byte
    dut.rinc.value = 1
    await RisingEdge(dut.rclk)
    await Timer(1, unit="ns")
    dut.rinc.value = 0

    # Check FIFO returns to empty
    assert int(dut.rempty.value) == 1, "FIFO should be empty after reading"

@cocotb.test()
async def test_fifo_ordering(dut):
    test_data = [0xA5, 0x3C, 0xF0, 0x12]

    # Initialize FIFO
    start_clocks(dut)
    await reset_fifo(dut)

    # Write all values
    for value in test_data:
        await write_fifo(dut, value)

    # Read and verify ordering
    for expected in test_data:
        actual = await read_fifo(dut)

        assert actual == expected, (
            f"Expected {expected:#04x}, got {actual:#04x}"
        )

    assert int(dut.rempty.value) == 1


@cocotb.test()
async def test_fifo_full(dut):
    test_data = [
        0xA5, 0x3C, 0xF0, 0x12,
        0xB6, 0x08, 0xF9, 0xD0,
        0xE4, 0xC8, 0x75, 0x89,
        0xA1, 0xE7, 0x15, 0x43
    ]

    start_clocks(dut)
    await reset_fifo(dut)

    # Write all 16 values
    for i, value in enumerate(test_data):
        await write_fifo(dut, value)

        # FIFO should not be full until the 16th write
        if i < len(test_data) - 1:
            assert int(dut.wfull.value) == 0, (
                f"FIFO became full after only {i + 1} writes"
            )

    # Verify FIFO is full
    assert int(dut.wfull.value) == 1, (
        "FIFO should be full after 16 writes"
    )

    # Attempt a 17th write while full
    await RisingEdge(dut.wclk)
    await Timer(1, unit="ns")

    dut.wdata.value = 0xFF
    dut.winc.value = 1

    await RisingEdge(dut.wclk)
    await Timer(1, unit="ns")

    dut.winc.value = 0

    # Verify FIFO remains full
    assert int(dut.wfull.value) == 1, (
        "FIFO should remain full after overflow attempt"
    )

    # Read all 16 values and verify ordering
    for i, expected in enumerate(test_data):
        actual = await read_fifo(dut)

        assert actual == expected, (
            f"Read {i + 1}: expected {expected:#04x}, "
            f"got {actual:#04x}"
        )

    # Verify FIFO is empty after all reads
    assert int(dut.rempty.value) == 1, (
        "FIFO should be empty after reading all 16 values"
    )


@cocotb.test()
async def test_fifo_underflow(dut):
    start_clocks(dut)
    await reset_fifo(dut)

    # FIFO should initially be empty.
    assert int(dut.rempty.value) == 1
    assert int(dut.wfull.value) == 0

    # Attempt five reads while empty.
    for i in range(5):
        await FallingEdge(dut.rclk)

        assert int(dut.rempty.value) == 1, (
            f"Empty flag deasserted before underflow {i + 1}"
        )

        dut.rinc.value = 1

        await RisingEdge(dut.rclk)
        await Timer(1, unit="ns")

        assert int(dut.rempty.value) == 1, (
            f"Empty flag cleared after underflow {i + 1}"
        )

        dut.rinc.value = 0

    # Verify normal operation still works.
    test_data = [0xA5, 0x3C, 0xF0]

    for value in test_data:
        await write_fifo(dut, value)

    for expected in test_data:
        actual = await read_fifo(dut)

        assert actual == expected, (
            f"Expected {expected:#04x}, got {actual:#04x}"
        )

    assert int(dut.rempty.value) == 1, (
        "FIFO should be empty after all valid reads"
    )
