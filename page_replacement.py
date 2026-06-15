"""
Module 3: Page Replacement Algorithms
Implements: FIFO, LRU, Optimal
"""


def fifo_page_replacement(pages, num_frames):
    frames = []
    faults = 0
    history = []

    for page in pages:
        if page not in frames:
            faults += 1
            if len(frames) < num_frames:
                frames.append(page)
            else:
                frames.pop(0)
                frames.append(page)
        history.append(list(frames))

    hits = len(pages) - faults
    hit_ratio = hits / len(pages) if pages else 0
    return history, faults, hit_ratio


def lru_page_replacement(pages, num_frames):
    frames = []
    faults = 0
    history = []
    recent = []  # tracks usage order, most recent at end

    for page in pages:
        if page in frames:
            recent.remove(page)
            recent.append(page)
        else:
            faults += 1
            if len(frames) < num_frames:
                frames.append(page)
            else:
                lru_page = recent.pop(0)
                idx = frames.index(lru_page)
                frames[idx] = page
            recent.append(page)
        history.append(list(frames))

    hits = len(pages) - faults
    hit_ratio = hits / len(pages) if pages else 0
    return history, faults, hit_ratio


def optimal_page_replacement(pages, num_frames):
    frames = []
    faults = 0
    history = []

    for i, page in enumerate(pages):
        if page in frames:
            history.append(list(frames))
            continue

        faults += 1
        if len(frames) < num_frames:
            frames.append(page)
        else:
            # find the page that won't be used for longest time / not used at all
            future = pages[i + 1:]
            farthest_idx = -1
            victim = frames[0]
            for f in frames:
                if f not in future:
                    victim = f
                    break
                else:
                    idx = future.index(f)
                    if idx > farthest_idx:
                        farthest_idx = idx
                        victim = f
            frames[frames.index(victim)] = page

        history.append(list(frames))

    hits = len(pages) - faults
    hit_ratio = hits / len(pages) if pages else 0
    return history, faults, hit_ratio


def frame_table_string(history, num_frames):
    """Render frame table as text, one column per reference."""
    lines = []
    for f in range(num_frames):
        row = []
        for state in history:
            row.append(str(state[f]) if f < len(state) else "-")
        lines.append(" | ".join(row))
    return "\n".join(lines)
