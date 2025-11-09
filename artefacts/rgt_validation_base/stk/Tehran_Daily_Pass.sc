stk.v.11.0
WrittenBy    formation-sat-exporter

BEGIN Scenario
    Name            Tehran_Daily_Pass

BEGIN Epoch

    Epoch           21 Mar 2026 07:34:25.000000000 UTCG

END Epoch

BEGIN Interval

    Start           21 Mar 2026 07:34:25.000000000 UTCG
    Stop            21 Mar 2026 07:45:55.000000000 UTCG

END Interval

BEGIN CentralBody

    PrimaryBody     Earth

END CentralBody

BEGIN AnalysisTimePeriod
    StartTime       21 Mar 2026 07:34:25.000000000 UTCG
    StopTime        21 Mar 2026 07:45:55.000000000 UTCG
END AnalysisTimePeriod

BEGIN Animation
    StartTime       21 Mar 2026 07:34:25.000000000 UTCG
    StopTime        21 Mar 2026 07:45:55.000000000 UTCG
    AnimationStep   1.000000
END Animation

BEGIN Assets
    Satellite       tehran_daily_pass.sat
END Assets
END Scenario
