# Asynchronous FIFO RTL Design & Verification

A parameterized, dual-clock asynchronous FIFO implemented in SystemVerilog and verified using Verilator and cocotb in a Linux environment via Windows Subsystem for Linux (WSL). Verible was also used for formatting and style linting.


The design is based on Clifford E. Cummings' asynchronous FIFO architecture and covers clock-domain crossing (CDC), Gray-coded pointer synchronization, full/empty flag generation, and Python-based RTL verification.

## Project status

The RTL implementation is complete for the current configuration. Initial directed verification passes, and additional verification is in progress.

## Features

- Parameterized data width (`DSIZE`) and address width (`ASIZE`)
- Independent read and write clock domains
- Gray-coded read and write pointers
- Two-stage pointer synchronizers for clock-domain crossing
- Full and empty flag generation
- Synchronous memory writes and asynchronous memory reads
- Configurable FIFO depth of `2^ASIZE` entries

Default configuration:

| Parameter | Value |
|---|---|
| Data width | 8 bits |
| Address width | 4 bits |
| FIFO depth | 16 entries |
| Write clock period (testbench) | 10 ns |
| Read clock period (testbench) | 14 ns |

## Architecture

The FIFO is divided into six modules:

| Module | Description |
|---|---|
| `fifo1.sv` | Top-level module connecting the FIFO components |
| `fifomem.sv` | Dual-port FIFO memory |
| `wptr_full.sv` | Write pointer and full detection |
| `rptr_empty.sv` | Read pointer and empty detection |
| `sync_r2w.sv` | Synchronizes the read pointer into the write clock domain |
| `sync_w2r.sv` | Synchronizes the write pointer into the read clock domain |

The pointers are Gray coded because only one bit changes between consecutive values, which reduces the risk of sampling an inconsistent multi-bit pointer across clock domains.

Two-stage synchronizers transfer the pointers between clock domains. Each flag is generated locally from the synchronized pointer of the opposite domain.

## Verification environment

The design is verified using:

- Verilator 5.055 for RTL linting and simulation
- cocotb 2.1.0 for testbenches
- Python for test automation and reusable verification helper functions

Helper functions cover clock generation, reset sequencing, FIFO writes, and FIFO reads.

### Directed test results

| Test | Description | Status |
|---|---|---|
| `test_fifo_basic` | Reset, single write/read, data integrity, and empty flag | PASS |
| `test_fifo_ordering` | Four sequential writes and reads, verifying FIFO ordering | PASS |
| `test_fifo_full` | Fill all 16 entries, check full flag, attempt overflow, and verify readback | PASS |

Current results: 3 tests passed, 0 failed.

The tests cover only these scenarios and are not exhaustive verification.

## Running the tests

### Prerequisites

- Linux or WSL Ubuntu
- Python 3
- Verilator
- cocotb

### Setup

Clone the repository and navigate to its directory.

Create a Python virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the Python dependencies:

```bash
python -m pip install -r requirements.txt
```

Verify Verilator is available:

```bash
verilator --version
```

Run Verilator lint:

```bash
verilator --lint-only -Wall --top-module fifo1 rtl/*.sv
```

### Simulation

Execute the cocotb test suite:

```bash
python run_tests.py
```

The runner compiles the SystemVerilog design using Verilator and executes the Python testbenches.

## Verification limitations and planned improvements

The current tests cover basic FIFO functionality and directed boundary conditions. 

Planned work:

- Directed tests for underflow protection, concurrent reads and writes, pointer wraparound, and mid-operation reset.
- A Python reference model and scoreboard that check data integrity and ordering automatically.
- Constrained-random transaction generation to cover more complex scenarios.
- SystemVerilog assertions on the FIFO control logic and flag behavior.
- Functional coverage metrics to show how complete the verification is and which scenarios are still untested.

## References

Clifford E. Cummings, *Simulation and Synthesis Techniques for Asynchronous FIFO Design*, SNUG San Jose, 2002.

The FIFO architecture is adapted from this paper. The RTL is adapted into SystemVerilog and comes with a cocotb verification environment.