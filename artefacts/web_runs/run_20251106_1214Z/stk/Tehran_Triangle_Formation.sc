stk.v.11.0
WrittenBy    formation-sat-exporter

BEGIN Scenario
    Name            Tehran_Triangle_Formation

BEGIN Epoch

    Epoch           20 Mar 2026 19:40:10.000000000

END Epoch

BEGIN Interval

    Start           20 Mar 2026 19:40:10.000000000
    Stop            21 Mar 2026 19:40:10.000000000

END Interval

BEGIN CentralBody

    PrimaryBody     Earth

END CentralBody

BEGIN AnalysisTimePeriod
    StartTime       20 Mar 2026 19:40:10.000000000
    StopTime        21 Mar 2026 19:40:10.000000000
END AnalysisTimePeriod

BEGIN Animation
    StartTime       20 Mar 2026 19:40:10.000000000
    StopTime        21 Mar 2026 19:40:10.000000000
    AnimationStep   1.000000
END Animation

BEGIN Assets
    Satellite       SAT_1.sat
    Satellite       SAT_2.sat
    Satellite       SAT_3.sat
    Facility        Facility_Tehran.fac
END Assets
END Scenario
