
from cocotb.utils import get_sim_time
from cocotb.triggers import FallingEdge, RisingEdge, Timer


async def monitor_writes(dut, scoreboard):
    while True:
        await FallingEdge(dut.wclk)
        await Timer(1, unit="ns")

        accepted = (
            int(dut.wrst_n.value) == 1
            and int(dut.winc.value) == 1
            and int(dut.wfull.value) == 0
        )

        if accepted:
            data = int(dut.wdata.value)

        await RisingEdge(dut.wclk)

        if accepted:
            scoreboard.record_write(
                data, get_sim_time(unit="ns")
            )


async def monitor_reads(dut, scoreboard):
    while True:
        await FallingEdge(dut.rclk)
        await Timer(1, unit="ns")

        accepted = (
            int(dut.rrst_n.value) == 1
            and int(dut.rinc.value) == 1
            and int(dut.rempty.value) == 0
        )

        if accepted:
            data = int(dut.rdata.value)

        await RisingEdge(dut.rclk)

        if accepted:
            scoreboard.check_read(
                data, get_sim_time(unit="ns")
            )
