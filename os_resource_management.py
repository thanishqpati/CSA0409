#!/usr/bin/env python3
"""
OS Resource Management Simulation – Online Exam Portal
======================================================
Implements:
  Part I  – CPU Scheduling  (FCFS, SJF-NP, Priority-NP, Round Robin)
  Part II – Memory Management (FIFO, LRU, Optimal page replacement)
  Part III– Disk Scheduling (FCFS, SSTF, SCAN, C-SCAN)

Parameters (Appendix I – Online Exam Portal):
  Processes : P1(0,4) P2(1,6) P3(2,3) P4(4,8) P5(5,2) | RR quantum = 2
  Memory    : RAM=2GB, Page size=4KB, Logical space=16MB, Frames=4
  Disk      : Cylinders 0-100, Head start=45,
              Queue = [12, 85, 33, 70, 95, 20, 60, 88]

Usage:
  python os_resource_management.py
  python os_resource_management.py --no-plot   # skip matplotlib plots

Requirements: Python 3.7+, matplotlib (optional for plots)
"""

from __future__ import annotations
import argparse
from collections import deque
from typing import List, Dict, Tuple, Any

# ---------------------------------------------------------------------------
# Optional plotting
# ---------------------------------------------------------------------------
try:
    import matplotlib.pyplot as plt
    HAS_MPL = True
except ImportError:
    HAS_MPL = False


# ===========================================================================
#  PART I – CPU SCHEDULING
# ===========================================================================

Process = Dict[str, Any]   # pid, arrival, burst, (priority)


def fcfs(processes: List[Process]) -> Tuple[List[Process], List[Tuple]]:
    """First-Come-First-Served (non-preemptive)."""
    procs = sorted([p.copy() for p in processes], key=lambda x: x["arrival"])
    time = 0
    gantt = []
    for p in procs:
        if time < p["arrival"]:
            time = p["arrival"]
        start = time
        time += p["burst"]
        p["finish"] = time
        p["tat"] = p["finish"] - p["arrival"]
        p["wt"] = p["tat"] - p["burst"]
        gantt.append((p["pid"], start, time))
    return procs, gantt


def sjf_np(processes: List[Process]) -> Tuple[List[Process], List[Tuple]]:
    """Shortest-Job-First (non-preemptive)."""
    procs = [p.copy() for p in processes]
    n = len(procs)
    time = 0
    completed = 0
    done = set()
    results = {}
    gantt = []

    while completed < n:
        available = [p for p in procs if p["arrival"] <= time and p["pid"] not in done]
        if not available:
            time = min(p["arrival"] for p in procs if p["pid"] not in done)
            continue
        available.sort(key=lambda x: x["burst"])
        p = available[0]
        start = time
        time += p["burst"]
        p["finish"] = time
        p["tat"] = p["finish"] - p["arrival"]
        p["wt"] = p["tat"] - p["burst"]
        results[p["pid"]] = p
        gantt.append((p["pid"], start, time))
        done.add(p["pid"])
        completed += 1
    return list(results.values()), gantt


def priority_np(processes: List[Process], priorities: Dict[str, int]
                ) -> Tuple[List[Process], List[Tuple]]:
    """Priority scheduling (non-preemptive). Lower number = higher priority."""
    procs = [p.copy() for p in processes]
    for p in procs:
        p["priority"] = priorities[p["pid"]]
    n = len(procs)
    time = 0
    completed = 0
    done = set()
    results = {}
    gantt = []

    while completed < n:
        available = [p for p in procs if p["arrival"] <= time and p["pid"] not in done]
        if not available:
            time = min(p["arrival"] for p in procs if p["pid"] not in done)
            continue
        available.sort(key=lambda x: x["priority"])
        p = available[0]
        start = time
        time += p["burst"]
        p["finish"] = time
        p["tat"] = p["finish"] - p["arrival"]
        p["wt"] = p["tat"] - p["burst"]
        results[p["pid"]] = p
        gantt.append((p["pid"], start, time))
        done.add(p["pid"])
        completed += 1
    return list(results.values()), gantt


def round_robin(processes: List[Process], quantum: int = 2
                ) -> Tuple[List[Process], List[Tuple]]:
    """Round-Robin (pre-emptive) with fixed quantum."""
    n = len(processes)
    # (pid, arrival, burst, remaining)
    procs = sorted(
        [(p["pid"], p["arrival"], p["burst"], p["burst"]) for p in processes],
        key=lambda x: x[1],
    )
    ready: deque = deque()
    time = 0
    completed = 0
    waiting = {p["pid"]: 0 for p in processes}
    turnaround = {p["pid"]: 0 for p in processes}
    finish: Dict[str, int] = {}
    gantt: List[Tuple] = []
    i = 0

    while completed < n:
        while i < n and procs[i][1] <= time:
            ready.append(procs[i])
            i += 1
        if not ready:
            if i < n:
                time = procs[i][1]
                continue
            break
        pid, arr, burst, rem = ready.popleft()
        exec_time = min(quantum, rem)
        start = time
        time += exec_time
        rem -= exec_time
        gantt.append((pid, start, time))
        while i < n and procs[i][1] <= time:
            ready.append(procs[i])
            i += 1
        if rem > 0:
            ready.append((pid, arr, burst, rem))
        else:
            completed += 1
            finish[pid] = time
            turnaround[pid] = time - arr
            waiting[pid] = turnaround[pid] - burst

    results = []
    for p in processes:
        results.append({
            "pid": p["pid"],
            "arrival": p["arrival"],
            "burst": p["burst"],
            "finish": finish[p["pid"]],
            "tat": turnaround[p["pid"]],
            "wt": waiting[p["pid"]],
        })
    return results, gantt


def print_cpu_results(name: str, results: List[Process], gantt: List[Tuple]):
    print(f"\n{'='*60}")
    print(f"  {name}")
    print(f"{'='*60}")
    print("Gantt Chart:", " → ".join(f"{pid}({s}-{e})" for pid, s, e in gantt))
    print(f"\n{'Process':<10}{'Arrival':<10}{'Burst':<8}{'Finish':<10}{'Waiting':<10}{'TAT':<8}")
    print("-" * 56)
    for r in sorted(results, key=lambda x: x["pid"]):
        print(f"{r['pid']:<10}{r['arrival']:<10}{r['burst']:<8}"
              f"{r['finish']:<10}{r['wt']:<10}{r['tat']:<8}")
    awt = sum(r["wt"] for r in results) / len(results)
    atat = sum(r["tat"] for r in results) / len(results)
    print(f"\nAverage Waiting Time     = {awt:.2f}")
    print(f"Average Turnaround Time  = {atat:.2f}")
    return awt, atat


# ===========================================================================
#  PART II – MEMORY MANAGEMENT (Page Replacement)
# ===========================================================================

def fifo_paging(refs: List[int], frames: int) -> int:
    mem: List[int] = []
    faults = 0
    for page in refs:
        if page not in mem:
            faults += 1
            if len(mem) < frames:
                mem.append(page)
            else:
                mem.pop(0)
                mem.append(page)
    return faults


def lru_paging(refs: List[int], frames: int) -> int:
    mem: List[int] = []
    faults = 0
    recent: Dict[int, int] = {}
    t = 0
    for page in refs:
        t += 1
        if page not in mem:
            faults += 1
            if len(mem) < frames:
                mem.append(page)
            else:
                victim = min(mem, key=lambda p: recent.get(p, 0))
                mem[mem.index(victim)] = page
        recent[page] = t
    return faults


def optimal_paging(refs: List[int], frames: int) -> int:
    mem: List[int] = []
    faults = 0
    for i, page in enumerate(refs):
        if page not in mem:
            faults += 1
            if len(mem) < frames:
                mem.append(page)
            else:
                future = {}
                for p in mem:
                    try:
                        future[p] = refs[i + 1:].index(p)
                    except ValueError:
                        future[p] = float("inf")
                victim = max(mem, key=lambda p: future[p])
                mem[mem.index(victim)] = page
    return faults


def memory_info(ram_gb: int, page_kb: int, logical_mb: int, frames: int):
    page_bytes = page_kb * 1024
    logical_bytes = logical_mb * 1024 * 1024
    total_frames = (ram_gb * 1024 ** 3) // page_bytes
    num_pages = logical_bytes // page_bytes
    print(f"\n{'='*60}")
    print("  MEMORY MANAGEMENT – PAGING PARAMETERS")
    print(f"{'='*60}")
    print(f"Physical RAM              = {ram_gb} GB")
    print(f"Page size                 = {page_kb} KB")
    print(f"Total frames in system    = {total_frames:,}")
    print(f"Frames allocated (demo)   = {frames}")
    print(f"Logical address space     = {logical_mb} MB")
    print(f"Pages per process         = {num_pages:,}")
    # Address translation example
    la = 0x12345
    print(f"\nAddress translation example:")
    print(f"  Logical address 0x{la:X} → page {la // page_bytes}, offset {la % page_bytes}")


# ===========================================================================
#  PART III – DISK SCHEDULING
# ===========================================================================

def disk_fcfs(queue: List[int], head: int) -> Tuple[int, List[int]]:
    seek = 0
    current = head
    seq = [head]
    for req in queue:
        seek += abs(req - current)
        current = req
        seq.append(req)
    return seek, seq


def disk_sstf(queue: List[int], head: int) -> Tuple[int, List[int]]:
    seek = 0
    current = head
    remaining = queue[:]
    seq = [head]
    while remaining:
        closest = min(remaining, key=lambda x: abs(x - current))
        seek += abs(closest - current)
        current = closest
        seq.append(closest)
        remaining.remove(closest)
    return seek, seq


def disk_scan(queue: List[int], head: int, max_cyl: int = 100
              ) -> Tuple[int, List[int]]:
    seek = 0
    current = head
    seq = [head]
    remaining = sorted(queue)
    right = [r for r in remaining if r >= current]
    left = [r for r in remaining if r < current]
    for r in right:
        seek += abs(r - current)
        current = r
        seq.append(r)
    if left:
        if current != max_cyl:
            seek += abs(max_cyl - current)
            current = max_cyl
            seq.append(max_cyl)
        for r in reversed(left):
            seek += abs(r - current)
            current = r
            seq.append(r)
    return seek, seq


def disk_cscan(queue: List[int], head: int, max_cyl: int = 100
               ) -> Tuple[int, List[int]]:
    seek = 0
    current = head
    seq = [head]
    remaining = sorted(queue)
    right = [r for r in remaining if r >= current]
    left = [r for r in remaining if r < current]
    for r in right:
        seek += abs(r - current)
        current = r
        seq.append(r)
    if left:
        if current != max_cyl:
            seek += abs(max_cyl - current)
            current = max_cyl
            seq.append(max_cyl)
        seek += max_cyl          # jump 100 → 0
        current = 0
        seq.append(0)
        for r in left:
            seek += abs(r - current)
            current = r
            seq.append(r)
    return seek, seq


def print_disk(name: str, seek: int, seq: List[int]):
    print(f"\n{name}:")
    print(f"  Sequence : {' → '.join(map(str, seq))}")
    print(f"  Total seek = {seek} cylinders")


# ===========================================================================
#  PLOTTING HELPERS
# ===========================================================================

def plot_gantt(gantt: List[Tuple], title: str, filename: str):
    if not HAS_MPL:
        return
    colors = {"P1": "#7EB6FF", "P2": "#90EE90", "P3": "#FFA07A",
              "P4": "#FFD700", "P5": "#DDA0DD"}
    fig, ax = plt.subplots(figsize=(12, 2.5))
    for pid, start, end in gantt:
        ax.barh(0, end - start, left=start, color=colors.get(pid, "gray"),
                edgecolor="black", height=0.5)
        ax.text((start + end) / 2, 0, pid, ha="center", va="center", fontsize=9)
    ax.set_yticks([])
    ax.set_xlabel("Time")
    ax.set_title(title)
    ax.set_xlim(0, max(e for _, _, e in gantt) + 1)
    ax.grid(axis="x", alpha=0.3)
    plt.tight_layout()
    plt.savefig(filename, dpi=120)
    plt.close()
    print(f"  [saved] {filename}")


def plot_disk_comparison(results: Dict[str, int], filename: str):
    if not HAS_MPL:
        return
    names = list(results.keys())
    seeks = list(results.values())
    fig, ax = plt.subplots(figsize=(7, 4))
    bars = ax.bar(names, seeks, color=["#ff9999", "#66b3ff", "#99ff99", "#ffcc99"])
    ax.set_ylabel("Total Seek (cylinders)")
    ax.set_title("Disk Scheduling – Seek Distance Comparison")
    for bar, s in zip(bars, seeks):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 4,
                str(s), ha="center", fontsize=10)
    plt.tight_layout()
    plt.savefig(filename, dpi=120)
    plt.close()
    print(f"  [saved] {filename}")


# ===========================================================================
#  MAIN
# ===========================================================================

def main():
    parser = argparse.ArgumentParser(description="OS Resource Management Simulation")
    parser.add_argument("--no-plot", action="store_true", help="Skip matplotlib plots")
    args = parser.parse_args()
    do_plot = HAS_MPL and not args.no_plot

    # ----- Process set (Appendix I) -----
    processes = [
        {"pid": "P1", "arrival": 0, "burst": 4},
        {"pid": "P2", "arrival": 1, "burst": 6},
        {"pid": "P3", "arrival": 2, "burst": 3},
        {"pid": "P4", "arrival": 4, "burst": 8},
        {"pid": "P5", "arrival": 5, "burst": 2},
    ]
    # Priority: lower number = higher priority (interactive urgency)
    priorities = {"P5": 1, "P3": 2, "P1": 3, "P2": 4, "P4": 5}
    quantum = 2

    print("=" * 60)
    print("  ONLINE EXAM PORTAL – OS RESOURCE MANAGEMENT SIMULATION")
    print("=" * 60)

    # ========== PART I ==========
    print("\n\n########## PART I – CPU SCHEDULING ##########")

    res, gantt = fcfs(processes)
    print_cpu_results("FCFS", res, gantt)

    res, gantt = sjf_np(processes)
    print_cpu_results("SJF (Non-Preemptive)", res, gantt)

    res, gantt = priority_np(processes, priorities)
    print_cpu_results("Priority (Non-Preemptive)", res, gantt)
    print(f"  Priorities used: {priorities}")

    res, gantt = round_robin(processes, quantum)
    print_cpu_results(f"Round Robin (quantum={quantum})", res, gantt)
    if do_plot:
        plot_gantt(gantt, f"Round Robin Gantt Chart (q={quantum})", "cpu_gantt_rr.png")

    # ========== PART II ==========
    print("\n\n########## PART II – MEMORY MANAGEMENT ##########")
    memory_info(ram_gb=2, page_kb=4, logical_mb=16, frames=4)

    refs = [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5, 1, 3]
    frames = 4
    print(f"\nReference string ({len(refs)} refs): {refs}")
    print(f"Frames = {frames}")
    f_fifo = fifo_paging(refs, frames)
    f_lru = lru_paging(refs, frames)
    f_opt = optimal_paging(refs, frames)
    print(f"\n  FIFO    page faults = {f_fifo}")
    print(f"  LRU     page faults = {f_lru}")
    print(f"  Optimal page faults = {f_opt}")

    # ========== PART III ==========
    print("\n\n########## PART III – DISK SCHEDULING ##########")
    head = 45
    queue = [12, 85, 33, 70, 95, 20, 60, 88]
    print(f"Head start = {head}")
    print(f"Request queue = {queue}")

    s_fcfs, seq_fcfs = disk_fcfs(queue, head)
    s_sstf, seq_sstf = disk_sstf(queue, head)
    s_scan, seq_scan = disk_scan(queue, head)
    s_cscan, seq_cscan = disk_cscan(queue, head)

    print_disk("FCFS", s_fcfs, seq_fcfs)
    print_disk("SSTF", s_sstf, seq_sstf)
    print_disk("SCAN", s_scan, seq_scan)
    print_disk("C-SCAN", s_cscan, seq_cscan)

    print(f"\n  Best (lowest seek) : SSTF = {s_sstf}")
    print(f"  Recommended       : SCAN  = {s_scan}  (fairness / no starvation)")

    if do_plot:
        plot_disk_comparison(
            {"FCFS": s_fcfs, "SSTF": s_sstf, "SCAN": s_scan, "C-SCAN": s_cscan},
            "disk_seek_comparison.png",
        )

    # ----- Final recommendation -----
    print("\n\n########## FINAL RECOMMENDATION ##########")
    print("  CPU  : Round Robin (quantum = 2) – fair, no starvation")
    print("  Mem  : Demand paging + LRU, working-set frame allocation")
    print("  Disk : SCAN (elevator) – good seek + fairness guarantee")
    print("  Files: Indexed allocation (Unix inode model)")
    print("\nDone.")


if __name__ == "__main__":
    main()
