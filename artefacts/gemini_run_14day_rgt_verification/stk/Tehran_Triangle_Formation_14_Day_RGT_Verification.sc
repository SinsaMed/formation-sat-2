stk.v.11.0
WrittenBy    formation-sat-exporter

BEGIN Scenario
    Name            Tehran_Triangle_Formation_14_Day_RGT_Verification

BEGIN Epoch

    Epoch           14 Mar 2026 07:40:10.000000000 UTCG

END Epoch

BEGIN Interval

    Start           14 Mar 2026 07:40:10.000000000 UTCG
    Stop            28 Mar 2026 07:40:10.000000000 UTCG

END Interval

BEGIN CentralBody

    PrimaryBody     Earth

END CentralBody

BEGIN AnalysisTimePeriod
    StartTime       14 Mar 2026 07:40:10.000000000 UTCG
    StopTime        28 Mar 2026 07:40:10.000000000 UTCG
END AnalysisTimePeriod

BEGIN Animation
    StartTime       14 Mar 2026 07:40:10.000000000 UTCG
    StopTime        28 Mar 2026 07:40:10.000000000 UTCG
    AnimationStep   1.000000
END Animation

BEGIN Assets
    Satellite       SAT_1.sat
    Satellite       SAT_2.sat
    Satellite       SAT_3.sat
    Facility        Facility_Tehran.fac
END Assets
END Scenario
