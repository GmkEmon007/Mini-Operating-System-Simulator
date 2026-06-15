"""
Module 6: File Management
Implements: Sequential Allocation, Linked Allocation, Indexed Allocation

Each function takes a list of files with their size in blocks and a total
disk size (number of blocks), and returns:
 - allocation table information
 - a disk block map: list of length `disk_size` where each entry is either
   None (free) or the file name occupying that block
"""

from copy import deepcopy


def sequential_allocation(files, disk_size):
    """
    files: list of dicts {"name": str, "size": int}  (size = number of blocks)
    Allocates contiguous blocks for each file (first-fit on free space).
    Returns: table (list of dicts with name, start, length, end), disk_map
    """
    disk_map = [None] * disk_size
    table = []

    for f in files:
        size = f["size"]
        start = _find_contiguous_free(disk_map, size)
        if start is None:
            table.append({"name": f["name"], "start": None, "length": size, "end": None, "ok": False})
            continue
        for b in range(start, start + size):
            disk_map[b] = f["name"]
        table.append({"name": f["name"], "start": start, "length": size, "end": start + size - 1, "ok": True})

    return table, disk_map


def _find_contiguous_free(disk_map, size):
    run_start = None
    run_len = 0
    for i, block in enumerate(disk_map):
        if block is None:
            if run_start is None:
                run_start = i
            run_len += 1
            if run_len == size:
                return run_start
        else:
            run_start = None
            run_len = 0
    return None


def linked_allocation(files, disk_size):
    """
    Allocates non-contiguous blocks linked via "pointers" (each block stores
    the index of the next block, -1 if it's the last).
    Returns: table (list of dicts with name, start, blocks, links), disk_map
    """
    disk_map = [None] * disk_size
    table = []
    free_blocks = [i for i in range(disk_size) if disk_map[i] is None]

    for f in files:
        size = f["size"]
        if len(free_blocks) < size:
            table.append({"name": f["name"], "start": None, "blocks": [], "links": {}, "ok": False})
            continue

        chosen = free_blocks[:size]
        free_blocks = free_blocks[size:]

        for b in chosen:
            disk_map[b] = f["name"]

        links = {}
        for idx in range(len(chosen)):
            links[chosen[idx]] = chosen[idx + 1] if idx + 1 < len(chosen) else -1

        table.append({"name": f["name"], "start": chosen[0], "blocks": chosen, "links": links, "ok": True})

    return table, disk_map


def indexed_allocation(files, disk_size):
    """
    Each file gets one index block whose pointers list the data blocks for
    that file. The index block itself is also marked as used on the disk map
    (shown separately in the table).
    Returns: table (list of dicts with name, index_block, data_blocks), disk_map
    """
    disk_map = [None] * disk_size
    table = []
    free_blocks = [i for i in range(disk_size)]

    for f in files:
        size = f["size"]
        needed = size + 1  # +1 for index block
        if len(free_blocks) < needed:
            table.append({"name": f["name"], "index_block": None, "data_blocks": [], "ok": False})
            continue

        index_block = free_blocks.pop(0)
        data_blocks = [free_blocks.pop(0) for _ in range(size)]

        disk_map[index_block] = f["name"] + "*"  # mark index block distinctly
        for b in data_blocks:
            disk_map[b] = f["name"]

        table.append({"name": f["name"], "index_block": index_block, "data_blocks": data_blocks, "ok": True})

    return table, disk_map


def disk_visualization(disk_map):
    """Return a simple textual representation of disk block allocation."""
    lines = []
    for i, block in enumerate(disk_map):
        status = block if block is not None else "Free"
        lines.append(f"Block {i:>3}: {status}")
    return "\n".join(lines)
