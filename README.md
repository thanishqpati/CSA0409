# OS Resource Management – Online Exam Portal

Simulation of **CPU Scheduling**, **Memory Management (Paging)** and **Disk Scheduling** for a real-time multi-user Online Exam Portal (Linux-based server).

## Parameters (Appendix I)

| Resource | Values |
|----------|--------|
| **Processes** | P1(0,4), P2(1,6), P3(2,3), P4(4,8), P5(5,2) |
| **RR Quantum** | 2 |
| **Memory** | RAM = 2 GB, Page size = 4 KB, Frames = 4, Logical space = 16 MB |
| **Disk** | Cylinders 0–100, Head start = 45 |
| **Request Queue** | 12, 85, 33, 70, 95, 20, 60, 88 |

## Features

### Part I – CPU Scheduling
- FCFS
- SJF (non-preemptive)
- Priority (non-preemptive) – priorities assigned by interactive urgency
- Round Robin (quantum = 2)
- Gantt charts, average waiting time & turnaround time

### Part II – Memory Management
- Page count & frame calculation
- Address translation example
- Page replacement: **FIFO**, **LRU**, **Optimal**
- Working-set / demand-paging discussion (in report)

### Part III – Disk Scheduling
- FCFS, SSTF, SCAN, C-SCAN
- Total seek distance comparison
- Recommendation based on fairness

## Requirements

```bash
Python 3.7+
matplotlib   # optional, only for plots
```

```bash
pip install matplotlib
```

## Run

```bash
# Full run (prints results + saves plots)
python os_resource_management.py

# Text-only (no plots)
python os_resource_management.py --no-plot
```

## Sample Output (abbreviated)

```
FCFS          AWT = 7.20   ATAT = 11.80
SJF (NP)      AWT = 4.60   ATAT =  9.20
Priority      AWT = 4.60   ATAT =  9.20
Round Robin   AWT = 8.80   ATAT = 13.40

Page faults (4 frames): FIFO=11  LRU=9  Optimal=6

Disk seek: FCFS=363  SSTF=116  SCAN=143  C-SCAN=188
```

## Final Recommendation

| Subsystem | Choice | Reason |
|-----------|--------|--------|
| CPU | **Round Robin (q=2)** | Fairness, no starvation, good response under concurrent load |
| Memory | Demand paging + **LRU** | Approximates locality; working-set frame allocation avoids thrashing |
| Disk | **SCAN** | Low seek + guaranteed progress (no starvation) |
| Files | **Indexed** (Unix inode) | Random question access + dynamic answer-script growth |

## Files

| File | Description |
|------|-------------|
| `os_resource_management.py` | Main simulation script (this repo) |
| `Online_Exam_Portal_Full_Project_Report.docx` | Full project report (15 sections) |

## License

MIT – free for academic use.
