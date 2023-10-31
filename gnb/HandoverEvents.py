from runtime.data_classes import HandoverParameters, ConditionalHandoverParameters


def check_a2_event(serving_rsrp):
    # Serving cell’s signal becomes weaker than the threshold
    if serving_rsrp < ConditionalHandoverParameters.a2_rsrp_threshold:
        return True
    return False


def check_a3_normal_event(serving, target):
    if serving < target + HandoverParameters.a3_offset:
        return True
    return False


def check_a3_prep_event_cho(serving, target):
    if serving < target + ConditionalHandoverParameters.prep_offset:
        return True
    return False


def check_a3_exec_event_cho(serving, target):
    if serving < target + ConditionalHandoverParameters.exec_offset:
        return True
    return False


def check_a4_event(target_rsrp):
    # Neighbor cell’s signal becomes stronger than the threshold
    if target_rsrp > ConditionalHandoverParameters.a4_rsrp_threshold:
        return True
    return False


def check_a5_event(serving, target):
    # Serving cell’s signal becomes weaker than the threshold 1 and neighbor cell’s signal becomes stronger than the threshold 2
    # todo: find values for threshold 1 and threshold 2
    pass
