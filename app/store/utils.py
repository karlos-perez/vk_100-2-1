
def is_message_from_chat(peer_id: int) -> bool:
    if peer_id > 2000000000:
        return True
    return False
