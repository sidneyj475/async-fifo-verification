# Asynchronous FIFO RTL Design & Verification

A parameterized, dual-clock asynchronous FIFO implemented in SystemVerilog and verified using Verilator and cocotb in a Linux environment via Windows Subsystem for Linux (WSL). Verible was also used for formatting and style linting.


The design is based on Clifford E. Cummings' asynchronous FIFO architecture and covers clock-domain crossing (CDC), Gray-coded pointer synchronization, full/empty flag generation, and Python-based RTL verification.

## Project status

The SystemVerilog RTL and the initial cocotb verification environment are finished for the default 8-bit, 16-entry configuration. All 13 tests pass, covering directed functional tests, scoreboard integration, and reproducible randomized traffic.

The design has only been checked in RTL simulation. FPGA implementation, formal verification, timing analysis, and physical CDC signoff have not been done.

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

The cocotb environment has:

- Transaction drivers: Reusable Python functions for clock generation, reset sequencing, FIFO writes, and FIFO reads.
- Transaction monitors: Observe accepted write and read transactions in their respective clock domains.
- Reference-model scoreboard: Uses a Python queue to compare accepted reads against previously accepted writes and verify FIFO ordering.
- Randomized stimulus: Generates independent write and read requests using reproducible random seeds.
- Directed tests: Exercise functional behavior, boundary conditions, clock ratios, and reset scenarios.

The scoreboard records transactions with simulation timestamps and evaluates them in chronological order.

### Test results

| Test | Description | Status |
|---|---|---|
| `test_fifo_basic` | Reset, single write/read, data integrity, and empty flag | PASS |
| `test_fifo_ordering` | Sequential writes and reads, verifying FIFO ordering | PASS |
| `test_fifo_full` | Fill all 16 entries, check full flag, attempt overflow, and verify readback | PASS |
| `test_fifo_underflow` | Verify underflow protection when FIFO is empty | PASS |
| `test_fifo_concurrent` | Concurrent read and write activity | PASS |
| `test_fifo_wraparound` | Repeated pointer wraparound and data ordering | PASS |
| `test_fifo_mid_reset` | Reset during FIFO operation | PASS |
| `test_fifo_fast_write` | Write clock faster than read clock | PASS |
| `test_fifo_fast_read` | Read clock faster than write clock | PASS |
| `test_fifo_equal_clocks` | Equal read and write clock periods | PASS |
| `test_fifo_unequal_clocks` | Unequal read and write clock periods | PASS |
| `test_scoreboard_integration` | Validate transaction monitors and reference-model scoreboard | PASS |
| `test_fifo_random` | Randomized read/write traffic with scoreboard checking | PASS |

### Randomized verification

The randomized test uses independent write and read traffic generators on separate clock domains.

Current configuration:

- Write clock period: 10 ns
- Read clock period: 14 ns
- Write request probability: 75%
- Read request probability: 75%
- Traffic generation: 500 write-clock cycles and 500 read-clock cycles
- Random seed: `20261101`

After generating traffic, the test drains the remaining FIFO contents and evaluates all recorded transactions with the scoreboard.

For the recorded seed, the test observed 268 accepted writes and 268 accepted reads with no scoreboard mismatches.

## Running the tests

### Prerequisites

- Linux or WSL Ubuntu
- Python 3
- Verilator (tested with 5.055)
- cocotb 2.1.0

### Setup

Clone the repository and navigate to its directory.

Create and activate a Python virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Verify Verilator is available:

```bash
verilator --version
```

Run RTL linting:

```bash
verilator --lint-only -Wall --top-module fifo1 rtl/*.sv
```

### Simulation

Run the complete cocotb regression:

```bash
python run_tests.py
```

The test runner builds the SystemVerilog design with Verilator and runs the directed, scoreboard integration, and randomized tests.

A successful regression reports 13 passing tests and exits with status code `0`.

## Verification limitations and planned improvements

The current verification environment covers the default FIFO configuration and selected functional scenarios. It does not establish exhaustive correctness or physical CDC safety.

Planned improvements:

- Execute randomized regressions across multiple seeds and clock ratios.
- Add SystemVerilog assertions for FIFO safety properties and full/empty flag behavior.
- Add functional coverage metrics for boundary conditions, pointer wraparound, reset, and concurrent operations.
- Verify additional FIFO parameter configurations.
- Explore formal verification of pointer and flag logic.
- Consider FPGA implementation and hardware testing.

## References

Clifford E. Cummings, *Simulation and Synthesis Techniques for Asynchronous FIFO Design*, SNUG San Jose, 2002.

The FIFO architecture is adapted from this paper. The RTL is adapted into SystemVerilog and comes with a cocotb verification environment.