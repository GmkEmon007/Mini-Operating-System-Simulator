"""
Module 5: Deadlock Handling - Banker's Algorithm
Includes safety check (safe sequence) and request handling.
"""

from copy import deepcopy


def calculate_need(max_matrix, alloc_matrix):
    need = []
    for i in range(len(max_matrix)):
        need.append([max_matrix[i][j] - alloc_matrix[i][j] for j in range(len(max_matrix[i]))])
    return need


def is_safe_state(available, max_matrix, alloc_matrix):
    """
    Returns (is_safe: bool, safe_sequence: list or None)
    """
    n = len(alloc_matrix)       # number of processes
    m = len(available)          # number of resource types

    need = calculate_need(max_matrix, alloc_matrix)
    work = list(available)
    finish = [False] * n
    safe_sequence = []

    while len(safe_sequence) < n:
        found = False
        for i in range(n):
            if not finish[i] and all(need[i][j] <= work[j] for j in range(m)):
                # process i can be satisfied
                for j in range(m):
                    work[j] += alloc_matrix[i][j]
                finish[i] = True
                safe_sequence.append(i)
                found = True
                break
        if not found:
            break

    if all(finish):
        return True, safe_sequence
    else:
        return False, None


def request_resources(process_id, request, available, max_matrix, alloc_matrix):
    """
    Attempts to grant a resource request from a process.
    Returns (granted: bool, message: str, new_available, new_alloc, safe_sequence)
    """
    n = len(alloc_matrix)
    m = len(available)
    need = calculate_need(max_matrix, alloc_matrix)

    # Step 1: request <= need
    for j in range(m):
        if request[j] > need[process_id][j]:
            return False, "Error: Request exceeds declared maximum need.", available, alloc_matrix, None

    # Step 2: request <= available
    for j in range(m):
        if request[j] > available[j]:
            return False, "Process must wait — resources not currently available.", available, alloc_matrix, None

    # Step 3: tentatively allocate
    new_available = list(available)
    new_alloc = deepcopy(alloc_matrix)
    for j in range(m):
        new_available[j] -= request[j]
        new_alloc[process_id][j] += request[j]

    safe, sequence = is_safe_state(new_available, max_matrix, new_alloc)

    if safe:
        return True, "Request granted. System remains in a safe state.", new_available, new_alloc, sequence
    else:
        return False, "Request denied. Granting it would lead to an unsafe state (possible deadlock).", available, alloc_matrix, None


def resource_allocation_table(processes, max_matrix, alloc_matrix, available):
    need = calculate_need(max_matrix, alloc_matrix)
    lines = []
    header = "Process | Allocation | Max | Need"
    lines.append(header)
    lines.append("-" * len(header))
    for i in range(len(processes)):
        lines.append(f"{processes[i]:7} | {alloc_matrix[i]} | {max_matrix[i]} | {need[i]}")
    lines.append("")
    lines.append(f"Available: {available}")
    return "\n".join(lines)
