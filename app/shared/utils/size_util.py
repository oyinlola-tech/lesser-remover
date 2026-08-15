def bytes_to_kb(size: int) -> float:
    return size / 1024


def bytes_to_mb(size: int) -> float:
    return size / (1024 * 1024)


def calculate_reduction(
    original_size: int,
    compressed_size: int,
) -> float:
    if original_size <= 0:
        return 0.0
    reduction = (
        (original_size - compressed_size)
        / original_size
    ) * 100
    return round(reduction, 2)
