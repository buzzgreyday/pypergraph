def ddag_to_dag(value: int):
    """Convert dDAG value to DAG value"""
    if value != 0:
        return float(value / 100000000)
    elif value == 0:
        return 0
    else:
        raise ValueError("Convert :: Balance can't be below 0.")