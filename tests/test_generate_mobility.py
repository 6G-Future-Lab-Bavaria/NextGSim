from mobility.GenerateMobility import GenerateMobility


def test_genetate_mobility_traces():
    mobility = GenerateMobility()
    filename = mobility.genetate_mobility_traces()
    assert type(filename) == str, "genetate_mobility_traces could not generate traces (Hint: check that passing floats, not int)"
