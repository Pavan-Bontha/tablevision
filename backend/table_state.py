from datetime import datetime

# In-memory floor state
floor_state = {}


def init_floor(config: dict):
    """Initialize floor state from restaurant config"""
    global floor_state
    floor_state = {}
    for table in config["tables"]:
        floor_state[table["table_id"]] = {
            "table_id": table["table_id"],
            "capacity": table["capacity"],
            "center_x": table["center_x"],
            "center_y": table["center_y"],
            "crop_box": table["crop_box"],
            "occupied_seats": 0,
            "has_people": False,
            "status": "available",
            "parties": [],
            "occupied_since": None,
            "estimated_minutes_remaining": None
        }


def update_table(table_id: int, vision_result: dict, avg_dining_minutes: int = 45):
    """Update a table's live state from vision result"""
    if table_id not in floor_state:
        return

    table = floor_state[table_id]
    prev_has_people = table["has_people"]

    table["occupied_seats"] = vision_result["occupied_seats"]
    table["has_people"] = vision_result["has_people"]

    # Table just became occupied — record timestamp
    if not prev_has_people and vision_result["has_people"]:
        table["occupied_since"] = datetime.now().isoformat()
        table["parties"] = [{"size": vision_result["occupied_seats"],
                             "occupied_since": table["occupied_since"]}]

    # Calculate estimated time remaining
    if table["occupied_since"]:
        elapsed = (datetime.now() - datetime.fromisoformat(table["occupied_since"])).seconds // 60
        remaining = avg_dining_minutes - elapsed
        table["estimated_minutes_remaining"] = max(0, remaining)

    # Assign status
    table["status"] = get_status(table)


def get_status(table: dict) -> str:
    cap = table["capacity"]
    seated = table["occupied_seats"]

    if not table["has_people"]:
        return "available"
    if seated >= cap:
        return "full"
    if cap == 2 and 0 < seated < cap:
        return "shareable"
    return "occupied"


def reset_table(table_id: int):
    """Manager manually resets a table to clearing state"""
    if table_id not in floor_state:
        return
    floor_state[table_id].update({
        "occupied_seats": 0,
        "has_people": False,
        "status": "clearing",
        "parties": [],
        "occupied_since": None,
        "estimated_minutes_remaining": None
    })


def get_floor_state() -> dict:
    return floor_state


def get_tables_for_party(party_size: int) -> list:
    """Find best tables for a given party size"""
    available = []
    predict = []

    for table in floor_state.values():
        cap = table["capacity"]
        status = table["status"]

        if party_size <= 2:
            if status == "available" and cap == 2:
                available.insert(0, table)
            elif status == "shareable" and cap == 2:
                available.append(table)
            elif status == "available" and cap > 2:
                available.append(table)
        else:
            if status == "available" and cap >= party_size:
                if cap == party_size:
                    available.insert(0, table)
                else:
                    available.append(table)

        if status in ["occupied", "full"] and table["estimated_minutes_remaining"] is not None:
            if cap >= party_size:
                predict.append(table)

    predict.sort(key=lambda t: t["estimated_minutes_remaining"])
    return {"immediate": available, "predicted": predict[:3]}
