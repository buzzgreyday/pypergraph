def ddag_to_dag(balance: int):
    """Convert dDAG value to DAG value"""
    if balance != 0:
        return float(balance / 100000000)
    elif balance == 0:
        return 0
    else:
        raise ValueError("Convert :: Balance can't be below 0.")