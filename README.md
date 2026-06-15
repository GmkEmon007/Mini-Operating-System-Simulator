# Mini Operating System Simulator 

A dark-themed Tkinter desktop application simulating six core Operating
System concepts. Everything runs in **one window**: a persistent left
sidebar lets you switch between pages instantly — no extra windows open.

## How to Run
```
python3 main.py
```

## Requirements
- Python 3.8+
- Tkinter (bundled with most Python installs; on Linux: `sudo apt-get install python3-tk`)

## Files
| File | Purpose |
|---|---|
| `main.py` | **Entry point.** Single window with sidebar + page switcher |
| `theme.py` | Shared dark theme, colors, fonts, sidebar widget |
| `dashboard_page.py` | Page: Dashboard (cards, charts, process table) |
| `cpu_page.py` | Page: CPU Scheduling (Gantt chart) |
| `memory_page.py` | Page: Memory Management (Paging + Fit strategies) |
| `sync_page.py` | Page: Process Synchronization (Dining Philosophers) |
| `deadlock_page.py` | Page: Deadlock Handling (Banker's Algorithm) |
| `file_page.py` | Page: File Management (Sequential/Linked/Indexed) |
| `scheduling.py` | Logic: FCFS, SJF, Round Robin, Priority Scheduling |
| `memory.py` | Logic: First/Best/Worst Fit, Paging |
| `page_replacement.py` | Logic: FIFO, LRU, Optimal page replacement |
| `synchronization.py` | Logic: Dining Philosophers (threaded), Producer-Consumer |
| `deadlock.py` | Logic: Banker's Algorithm (safety check, request handling) |
| `file_management.py` | Logic: Sequential, Linked, Indexed file allocation |

## How Navigation Works
`main.py` creates one `Tk()` window containing:
- A persistent `Sidebar` (from `theme.py`) on the left
- A content `Frame` on the right where every page is pre-built and stacked
  on top of each other using `grid(row=0, column=0, sticky="nsew")`

Clicking a sidebar item calls `show_page(key)`, which simply calls
`page.tkraise()` to bring that page to the front — instant switching, no new
windows, and all pages retain their state (e.g. the Gantt chart you ran
stays there when you come back).

## Module Overview

### 1. Dashboard
Summary cards (total/running/waiting processes, CPU utilization), a live
CPU utilization line chart, a process-status pie chart, and a recent
processes table.

### 2. CPU Scheduling
FCFS, SJF, Round Robin, and Priority Scheduling. Editable process table
(double-click any cell), Gantt chart visualization, and metrics: average
waiting time, average turnaround time, CPU utilization, throughput.

### 3. Memory Management
Two tabs:
- **Paging / Page Replacement** — FIFO, LRU, Optimal with a frame table
  visualization (faults highlighted), fault row, and statistics panel.
- **Block Allocation** — First Fit, Best Fit, Worst Fit with memory block
  visualization and a fragmentation report.

### 4. Process Synchronization
Dining Philosophers problem, simulated with real Python threads and locks
(mutexes) to represent forks. Circular visualization shows each
philosopher's state (Thinking/Hungry/Eating) with a live log. Controls:
number of philosophers, simulation speed, Start/Pause/Reset.

### 5. Deadlock Handling (Banker's Algorithm)
Editable Max / Allocation / Need matrices and Available vector. "Check Safe
State" computes a safe sequence (or reports deadlock). "Resource Request
Simulation" lets you submit a request for a process; it's validated against
Need and Available, then checked for safety before being granted.

### 6. File Management
Sequential, Linked, and Indexed allocation. Editable file directory (name +
size in blocks), disk size configuration, allocation table specific to the
chosen method, and a color-coded disk block visualization with legend.

## Notes
- The Dining Philosophers simulation runs in background daemon threads.
  Use Reset on that page before closing the app for a clean stop (daemon
  threads will also exit automatically when the process ends).
- Switching away from the Synchronization page does not pause the
  simulation — it continues running in the background and resumes
  animating when you switch back.
