#!/usr/bin/env python3
"""Protocol schema generator and verification tool.

Inspects registered packet definitions across protocol states,
detects duplicate packet IDs or direction conflicts, and generates
summary reports or JSON schemas.
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Dict, List

from mineflex.constants import (
    DEFAULT_PROTOCOL_VERSION,
    SUPPORTED_VERSIONS,
    ProtocolState,
)
from mineflex.protocol.registry import ProtocolRegistry


def inspect_protocol(protocol_version: int) -> Dict[str, Any]:
    """Inspect all registered packets for a given protocol version."""
    registry = ProtocolRegistry.for_version(protocol_version)

    conflicts: List[Dict[str, Any]] = []
    packets_by_state: Dict[str, Dict[str, List[Dict[str, Any]]]] = {}

    seen_ids: Dict[tuple[ProtocolState, bool, int], str] = {}

    # Gather registered packets from registry internals
    for (state, is_sb, pkt_id), pkt_cls in registry._packets_by_id.items():
        state_name = state.name
        direction = "serverbound" if is_sb else "clientbound"

        if state_name not in packets_by_state:
            packets_by_state[state_name] = {"clientbound": [], "serverbound": []}

        pkt_info = {
            "name": pkt_cls.name,
            "id": f"0x{pkt_id:02X}",
            "id_int": pkt_id,
            "class": pkt_cls.__name__,
            "module": pkt_cls.__module__,
        }
        packets_by_state[state_name][direction].append(pkt_info)

        # Check for ID collisions
        key = (state, is_sb, pkt_id)
        if key in seen_ids and seen_ids[key] != pkt_cls.name:
            conflicts.append({
                "state": state_name,
                "direction": direction,
                "id": f"0x{pkt_id:02X}",
                "packet_1": seen_ids[key],
                "packet_2": pkt_cls.name,
            })
        else:
            seen_ids[key] = pkt_cls.name

    # Sort packets by ID for clean reporting
    for state_name, dirs in packets_by_state.items():
        for dir_name in dirs:
            dirs[dir_name].sort(key=lambda p: p["id_int"])

    total_packets = len(seen_ids)

    return {
        "protocol_version": protocol_version,
        "total_packets": total_packets,
        "conflicts": conflicts,
        "has_conflicts": len(conflicts) > 0,
        "states": packets_by_state,
    }


def print_human_report(report: Dict[str, Any]) -> None:
    """Print formatted terminal report."""
    print("=" * 60)
    print(f" Mineflex Protocol Report - Protocol Version {report['protocol_version']}")
    print("=" * 60)
    print(f"Total Registered Codecs: {report['total_packets']}")
    print(f"Conflicts Detected:      {len(report['conflicts'])}")
    print("-" * 60)

    for state, dirs in report["states"].items():
        print(f"\n[{state}]")
        for direction, pkts in dirs.items():
            dir_label = "Serverbound (C->S)" if direction == "serverbound" else "Clientbound (S->C)"
            print(f"  {dir_label} ({len(pkts)} packets):")
            for pkt in pkts:
                print(f"    {pkt['id']} : {pkt['name']:<35} ({pkt['class']})")

    if report["conflicts"]:
        print("\n" + "!" * 60)
        print(" CONFLICTS DETECTED:")
        for c in report["conflicts"]:
            print(
                f"  [{c['state']}] {c['direction']} ID {c['id']}: "
                f"{c['packet_1']} vs {c['packet_2']}"
            )
        print("!" * 60)
    else:
        print("\n[OK] No packet ID collisions detected.")


def main() -> int:
    parser = argparse.ArgumentParser(description="Mineflex Protocol Registry Inspector")
    parser.add_argument(
        "--version",
        type=int,
        default=DEFAULT_PROTOCOL_VERSION,
        help=f"Protocol version (default: {DEFAULT_PROTOCOL_VERSION})",
    )
    parser.add_argument(
        "--all-versions",
        action="store_true",
        help="Inspect all supported protocol versions",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Run conflict check and exit with non-zero if collisions exist",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output raw JSON format",
    )

    args = parser.parse_args()

    versions = sorted(set(SUPPORTED_VERSIONS.values())) if args.all_versions else [args.version]
    overall_conflicts = 0

    for ver in versions:
        report = inspect_protocol(ver)
        if report["has_conflicts"]:
            overall_conflicts += len(report["conflicts"])

        if args.json:
            print(json.dumps(report, indent=2))
        else:
            print_human_report(report)

    if args.check and overall_conflicts > 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
