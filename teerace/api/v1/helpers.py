def get_filtered_checkpoints(checkpoints):
    try:
        return ";".join([v for v in checkpoints.split(";") if float(v) != 0.0])
    except ValueError:
        return ""
