import re
from collections import defaultdict
from pathlib import Path

# Define the regex patterns
HEADER_PATTERN = re.compile(r'^#(\d+) - (\d+)s(?: - (\w+))?$')
DATA_PATTERN = re.compile(r'round:\s*(\d+);\s*currentMeasure:\s*([\d.]+);\s*elapsed:\s*(\d+)')
SECTION_HEADER_PATTERN = re.compile(r'^##\s*(.*)$')

def parse_boat_file(filepath: Path):
    runs = []
    current_section = None
    current_run = None
    is_invalid = False

    with filepath.open() as f:
        for line in f:
            line = line.strip()

            # Detect attachment section (e.g., ## ATTACHED TO RIGHT)
            section_match = SECTION_HEADER_PATTERN.match(line)
            if section_match:
                current_section = section_match.group(1).strip()
                continue

            # Detect run header (e.g., #1 - 30s - invalid)
            header_match = HEADER_PATTERN.match(line)
            if header_match:
                if current_run:
                    runs.append(current_run)
                run_number, duration, status = header_match.groups()
                is_invalid = status == 'invalid'

                current_run = {
                    "section": current_section,
                    "run_number": int(run_number),
                    "duration_s": int(duration),
                    "invalid": is_invalid,
                    "measurements": []
                }
                continue

            # Detect measurement line
            data_match = DATA_PATTERN.match(line)
            if data_match:
                round_num, measure, elapsed = data_match.groups()
                current_run["measurements"].append({
                    "current_measure": float(measure),
                    "elapsed_ms": int(elapsed)
                })

        # Add last run
        if current_run:
            runs.append(current_run)

    return runs
