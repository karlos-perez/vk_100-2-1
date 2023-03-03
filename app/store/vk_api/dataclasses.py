from dataclasses import dataclass


@dataclass
class UpdateObject:
    id: int
    from_id: int
    peer_id: int
    text: str


@dataclass
class Update:
    type: str
    object: dict


def to_list_dt(raw_updates: list[dict]) -> list[Update]:
    updates = []
    for update in raw_updates:
        updates.append(Update(type=update["type"], object=update["object"]))
    return updates
