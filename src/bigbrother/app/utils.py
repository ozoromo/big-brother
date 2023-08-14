def formatSeconds(seconds):
    if not isinstance(seconds, (int, float)) or seconds < 0:
        return "Invalid input"

    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    remaining_seconds = int(seconds % 60)

    formatted_time_parts = []

    if hours > 0:
        formatted_time_parts.append(f"{hours}h")

    if minutes > 0:
        formatted_time_parts.append(f"{minutes}m")

    if remaining_seconds > 0:
        formatted_time_parts.append(f"{remaining_seconds}s")

    return "".join(formatted_time_parts)
