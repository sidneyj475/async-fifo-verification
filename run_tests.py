from pathlib import Path
from cocotb_tools.runner import get_runner

root = Path(__file__).resolve().parent

runner = get_runner("verilator")

runner.build(
    sources=list((root / "rtl").glob("*.sv")),
    hdl_toplevel="fifo1",
    build_dir=str(root / "sim_build"),
    always=True,
)

runner.test(
    hdl_toplevel="fifo1",
    test_module=["test_fifo",
        "test_fifo_scoreboard",
        "test_fifo_random",
    ],
    test_dir=str(root / "tb"),
    
)
