"""
Module 1: CPU Scheduling Simulator
Implements: FCFS, SJF (non-preemptive), Round Robin, Priority Scheduling
"""

from copy import deepcopy


def fcfs(processes):
    """First Come First Serve.
    processes: list of dicts with pid, arrival, burst
    returns: gantt list of (pid, start, end), and updated processes with wt/tat
    """
    procs = deepcopy(processes)
    procs.sort(key=lambda p: p["arrival"])
    time = 0
    gantt = []
    for p in procs:
        start = max(time, p["arrival"])
        end = start + p["burst"]
        p["start"] = start
        p["end"] = end
        p["wt"] = start - p["arrival"]
        p["tat"] = end - p["arrival"]
        gantt.append((p["pid"], start, end))
        time = end
    return gantt, procs


def sjf_non_preemptive(processes):
    """Shortest Job First (non-preemptive)."""
    procs = deepcopy(processes)
    n = len(procs)
    completed = 0
    time = 0
    done = [False] * n
    gantt = []

    while completed < n:
        idx = -1
        min_burst = float("inf")
        for i, p in enumerate(procs):
            if not done[i] and p["arrival"] <= time and p["burst"] < min_burst:
                min_burst = p["burst"]
                idx = i
        if idx == -1:
            # CPU idle, jump to next arrival
            next_arrival = min(p["arrival"] for i, p in enumerate(procs) if not done[i])
            time = next_arrival
            continue

        p = procs[idx]
        start = time
        end = start + p["burst"]
        p["start"] = start
        p["end"] = end
        p["wt"] = start - p["arrival"]
        p["tat"] = end - p["arrival"]
        gantt.append((p["pid"], start, end))
        time = end
        done[idx] = True
        completed += 1

    return gantt, procs


def round_robin(processes, quantum):
    """Round Robin Scheduling."""
    procs = deepcopy(processes)
    n = len(procs)
    remaining = {p["pid"]: p["burst"] for p in procs}
    arrival = {p["pid"]: p["arrival"] for p in procs}

    procs_sorted = sorted(procs, key=lambda p: p["arrival"])
    queue = []
    gantt = []
    time = 0
    visited = set()
    completed = {}

    # push first arriving process(es)
    i = 0
    if procs_sorted:
        time = procs_sorted[0]["arrival"]
        while i < n and procs_sorted[i]["arrival"] <= time:
            queue.append(procs_sorted[i]["pid"])
            visited.add(procs_sorted[i]["pid"])
            i += 1

    while queue:
        pid = queue.pop(0)
        exec_time = min(quantum, remaining[pid])
        start = time
        end = time + exec_time
        gantt.append((pid, start, end))
        time = end
        remaining[pid] -= exec_time

        # add newly arrived processes during this execution
        while i < n and procs_sorted[i]["arrival"] <= time:
            queue.append(procs_sorted[i]["pid"])
            visited.add(procs_sorted[i]["pid"])
            i += 1

        if remaining[pid] > 0:
            queue.append(pid)
        else:
            completed[pid] = end

        # if queue empty but processes remain, jump time to next arrival
        if not queue and i < n:
            time = max(time, procs_sorted[i]["arrival"])
            while i < n and procs_sorted[i]["arrival"] <= time:
                queue.append(procs_sorted[i]["pid"])
                visited.add(procs_sorted[i]["pid"])
                i += 1

    for p in procs:
        p["end"] = completed[p["pid"]]
        p["tat"] = p["end"] - p["arrival"]
        p["wt"] = p["tat"] - p["burst"]

    return gantt, procs


def priority_scheduling(processes, preemptive=False):
    """Priority Scheduling (non-preemptive by default). Lower number = higher priority."""
    if preemptive:
        return _priority_preemptive(processes)

    procs = deepcopy(processes)
    n = len(procs)
    completed = 0
    time = 0
    done = [False] * n
    gantt = []

    while completed < n:
        idx = -1
        best_priority = float("inf")
        for i, p in enumerate(procs):
            if not done[i] and p["arrival"] <= time and p["priority"] < best_priority:
                best_priority = p["priority"]
                idx = i
        if idx == -1:
            next_arrival = min(p["arrival"] for i, p in enumerate(procs) if not done[i])
            time = next_arrival
            continue

        p = procs[idx]
        start = time
        end = start + p["burst"]
        p["start"] = start
        p["end"] = end
        p["wt"] = start - p["arrival"]
        p["tat"] = end - p["arrival"]
        gantt.append((p["pid"], start, end))
        time = end
        done[idx] = True
        completed += 1

    return gantt, procs


def _priority_preemptive(processes):
    procs = deepcopy(processes)
    n = len(procs)
    remaining = {p["pid"]: p["burst"] for p in procs}
    arrival = {p["pid"]: p["arrival"] for p in procs}
    priority = {p["pid"]: p["priority"] for p in procs}

    time = 0
    completed = {}
    gantt = []
    last_pid = None
    max_time = sum(p["burst"] for p in procs) + max(p["arrival"] for p in procs) + 1

    while len(completed) < n and time <= max_time:
        candidates = [pid for pid in remaining if remaining[pid] > 0 and arrival[pid] <= time]
        if not candidates:
            time += 1
            continue
        pid = min(candidates, key=lambda x: priority[x])

        if gantt and gantt[-1][0] == pid:
            gantt[-1] = (pid, gantt[-1][1], gantt[-1][2] + 1)
        else:
            gantt.append((pid, time, time + 1))

        remaining[pid] -= 1
        time += 1
        if remaining[pid] == 0:
            completed[pid] = time

    for p in procs:
        p["end"] = completed[p["pid"]]
        p["tat"] = p["end"] - p["arrival"]
        p["wt"] = p["tat"] - p["burst"]

    return gantt, procs


def calculate_averages(procs):
    avg_wt = sum(p["wt"] for p in procs) / len(procs)
    avg_tat = sum(p["tat"] for p in procs) / len(procs)
    return avg_wt, avg_tat


def gantt_to_string(gantt):
    """Render a simple text Gantt chart."""
    top = "| "
    bottom = ""
    for pid, start, end in gantt:
        width = max(len(str(pid)), len(str(end))) + 2
        top += f"{pid}".center(width) + "| "
    line1 = top
    line2 = f"{gantt[0][1]}".ljust(0)

    # second line with time markers
    times = [gantt[0][1]] + [g[2] for g in gantt]
    line2 = "".join(f"{t}".ljust(len(f'{gantt[i][0]}'.center(max(len(str(gantt[i][0])), len(str(gantt[i][2])))+2)+'| ')) if i < len(gantt) else f"{t}"
                     for i, t in enumerate(times))
    return line1 + "\n" + " ".join(str(t) for t in times)
