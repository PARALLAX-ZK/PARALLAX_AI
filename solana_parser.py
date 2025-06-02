import logging
from typing import List, Dict, Optional, Any

logger = logging.getLogger("SOLANA_PARSER")

TRIGGER_PREFIX = "Program log: AITrigger::"
RESULT_PREFIX = "Program log: ResultReady::"
ERROR_PREFIX = "Program log: Error::"

class ParsedEvent:
    def __init__(self, slot: int, event_type: str, data: Dict[str, Any]):
        self.slot = slot
        self.event_type = event_type
        self.data = data

    def __repr__(self):
        return f"[{self.slot}] {self.event_type}: {self.data}"

def parse_log_line(line: str) -> Optional[Dict[str, str]]:
    if "::" not in line:
        return None
    parts = line.split("::", 1)
    if len(parts) != 2:
        return None
    try:
        tag, payload = parts
        data = {}
        for item in payload.strip().split(";"):
            if "=" in item:
                k, v = item.split("=", 1)
                data[k.strip()] = v.strip()
        return data
    except Exception as e:
        logger.error(f"Failed to parse line: {line} - {e}")
        return None

def parse_transaction_logs(slot: int, logs: List[str]) -> List[ParsedEvent]:
    parsed_events = []

    for line in logs:
        if TRIGGER_PREFIX in line:
            data = parse_log_line(line.replace(TRIGGER_PREFIX, ""))
            if data:
                parsed_events.append(ParsedEvent(slot, "AI_TRIGGER", data))
        elif RESULT_PREFIX in line:
            data = parse_log_line(line.replace(RESULT_PREFIX, ""))
            if data:
                parsed_events.append(ParsedEvent(slot, "RESULT_READY", data))
        elif ERROR_PREFIX in line:
            data = parse_log_line(line.replace(ERROR_PREFIX, ""))
            if data:
                parsed_events.append(ParsedEvent(slot, "ERROR", data))

    return parsed_events

def extract_events_from_log_block(log_block: Dict[str, Any]) -> List[ParsedEvent]:
    if not log_block or "logs" not in log_block or "slot" not in log_block:
        return []

    slot = log_block["slot"]
    logs = log_block["logs"]
    return parse_transaction_logs(slot, logs)

if __name__ == "__main__":
    example_logs = [
        "Program log: AITrigger::task_id=abc123; model_id=parallax-llm-v1; input=Analyze BTC today",
        "Program log: ResultReady::task_id=abc123; output_hash=5fe29a; status=ok",
        "Program log: Error::task_id=abc123; reason=model_not_found"
    ]

    slot_number = 123456
    events = parse_transaction_logs(slot_number, example_logs)
    for event in events:
        print(event)
