def friend_chati_session_id(self_id: int, supplicant: int) -> str:
    return f"qq-friend-{self_id}-{supplicant}"


def group_chati_session_id(self_id: int, supplicant: int) -> str:
    return f"qq-group-{self_id}-{supplicant}"
