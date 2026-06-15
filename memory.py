"""
Module 2: Memory Management
Implements: First Fit, Best Fit, Worst Fit, Paging
"""

from copy import deepcopy


def fixed_partition_allocation(blocks, processes, strategy="first"):
    """
    blocks: list of ints (sizes of memory blocks)
    processes: list of ints (sizes of processes)
    strategy: 'first', 'best', 'worst'
    returns: allocation map {process_index: block_index or None}, remaining block sizes
    """
    block_sizes = deepcopy(blocks)
    allocation = {}
    occupied = [False] * len(block_sizes)

    for i, proc_size in enumerate(processes):
        candidates = [
            (j, block_sizes[j]) for j in range(len(block_sizes))
            if not occupied[j] and block_sizes[j] >= proc_size
        ]
        if not candidates:
            allocation[i] = None
            continue

        if strategy == "first":
            chosen = candidates[0][0]
        elif strategy == "best":
            chosen = min(candidates, key=lambda x: x[1])[0]
        elif strategy == "worst":
            chosen = max(candidates, key=lambda x: x[1])[0]
        else:
            raise ValueError("Unknown strategy")

        allocation[i] = chosen
        occupied[chosen] = True

    return allocation, block_sizes


def fragmentation_report(blocks, processes, allocation):
    """Compute internal fragmentation per allocated block and external fragmentation total."""
    internal_frag = {}
    used_blocks = set()
    for i, block_idx in allocation.items():
        if block_idx is not None:
            internal_frag[i] = blocks[block_idx] - processes[i]
            used_blocks.add(block_idx)

    external_frag = sum(
        blocks[j] for j in range(len(blocks)) if j not in used_blocks
    )
    return internal_frag, external_frag


def paging_allocation(process_size, page_size, num_frames):
    """
    Simulate paging: split process into pages, assign to free frames.
    Returns page table {page_num: frame_num or None}, num pages required.
    """
    num_pages = (process_size + page_size - 1) // page_size
    page_table = {}
    for p in range(num_pages):
        if p < num_frames:
            page_table[p] = p  # simplistic 1-1 mapping for free frames
        else:
            page_table[p] = None  # not enough frames
    last_page_size = process_size - (num_pages - 1) * page_size
    internal_frag = page_size - last_page_size if last_page_size != page_size else 0
    return page_table, num_pages, internal_frag


def memory_visualization(blocks, processes, allocation):
    """Return a textual visualization of memory blocks and their allocation status."""
    lines = []
    for j, size in enumerate(blocks):
        assigned = [i for i, b in allocation.items() if b == j]
        if assigned:
            pid = assigned[0]
            used = processes[pid]
            free = size - used
            lines.append(
                f"Block {j} [Size={size}]: Allocated to P{pid} "
                f"(used={used}, internal frag={free})"
            )
        else:
            lines.append(f"Block {j} [Size={size}]: FREE (external frag)")
    return "\n".join(lines)
