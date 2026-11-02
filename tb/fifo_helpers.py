
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import FallingEdge, RisingEdge, Timer


def start_clocks(dut, wperiod=10, rperiod=14):
    # Start write and read clocks
    dut.wclk.value = 0
    dut.rclk.value = 0

    cocotb.start_soon(
        Clock(dut.wclk, wperiod, unit="ns").start()
    )
    cocotb.start_soon(
        Clock(dut.rclk, rperiod, unit="ns").start()
    )


async def reset_fifo(dut):
    # Reset both FIFO clock domains
    dut.winc.value = 0
    dut.rinc.value = 0
    dut.wdata.value = 0
    dut.wrst_n.value = 0
    dut.rrst_n.value = 0

    # Allow both clock domains to reset
    await Timer(50, unit="ns")

    assert int(dut.rempty.value) == 1
    assert int(dut.wfull.value) == 0

    dut.wrst_n.value = 1
    dut.rrst_n.value = 1

    await Timer(50, unit="ns")


async def write_fifo(dut, value):
    # Write exactly one word when FIFO is not full
    await FallingEdge(dut.wclk)

    assert int(dut.wfull.value) == 0, (
        "Cannot write: FIFO is full"
    )

    dut.wdata.value = value
    dut.winc.value = 1

    await RisingEdge(dut.wclk)
    await Timer(1, unit="ns")

    dut.winc.value = 0


async def read_fifo(dut, timeout_cycles=10):
    # Wait for data, then consume exactly one word

    for _ in range(timeout_cycles):
        await FallingEdge(dut.rclk)

        if int(dut.rempty.value) == 0:
            break
    else:
        raise AssertionError("Timed out waiting for FIFO data")

    # First-word fall-through: data is available
    # before the read pointer advances.
    expected_data = int(dut.rdata.value)

    dut.rinc.value = 1

    await RisingEdge(dut.rclk)
    await Timer(1, unit="ns")

    dut.rinc.value = 0

    return expected_data

