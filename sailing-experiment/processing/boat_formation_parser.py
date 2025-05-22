import re
from pathlib import Path
from typing import List

# Patterns
SECTION_PATTERN = re.compile(r'^##\s*(.*)$')
HEADER_PATTERN = re.compile(r'^#(\d+)\s*-\s*(\d+)s\s*-\s*boat-(\d+)', re.IGNORECASE)
DATA_PATTERN = re.compile(r'round:\s*\d+;\s*currentMeasure:\s*([-]?\d+\.\d+);\s*elapsed:\s*(\d+)')

def parse_group_run_file(filepath: Path) -> List[dict]:
    runs = []
    current_section = None
    current_run = None

    with filepath.open() as f:
        for line in f:
            line = line.strip()

            # Section header like ## 1,2,3 - left
            section_match = SECTION_PATTERN.match(line)
            if section_match:
                current_section = section_match.group(1).strip()
                continue

            # Run header like #1 - 45s - boat-1
            header_match = HEADER_PATTERN.match(line)
            if header_match:
                if current_run:
                    runs.append(current_run)

                run_number, duration_s, boat_id = header_match.groups()
                current_run = {
                    "section": current_section,
                    "run_number": int(run_number),
                    "duration_s": int(duration_s),
                    "boat_id": f"boat-{boat_id}",
                    "invalid": False,  # optional: you can parse an "invalid" flag if needed
                    "measurements": [],
                }
                continue

            # Measurement line
            data_match = DATA_PATTERN.match(line)
            if data_match and current_run:
                current, elapsed = data_match.groups()

                # Convert to absolute value
                abs_current = abs(float(current))

                current_run["measurements"].append({
                    "current_measure": abs_current,
                    "elapsed_ms": int(elapsed),
                    "watt": abs_current * 11.1,
                })

        # Append final run
        if current_run:
            runs.append(current_run)

    return runs
