stk.v.11.0
WrittenBy    formation-sat-exporter

BEGIN Scenario
    Name            Tehran_Daily_Pass

BEGIN Epoch

    Epoch           21 Mar 2026 09:32:00.000000000

END Epoch

BEGIN Interval

    Start           21 Mar 2026 09:32:00.000000000
    Stop            28 Mar 2026 00:00:00.000000000

END Interval

BEGIN CentralBody

    PrimaryBody     Earth

END CentralBody

BEGIN AnalysisTimePeriod
    StartTime       21 Mar 2026 09:32:00.000000000
    StopTime        28 Mar 2026 00:00:00.000000000
END AnalysisTimePeriod

BEGIN Animation
    StartTime       21 Mar 2026 09:32:00.000000000
    StopTime        28 Mar 2026 00:00:00.000000000
    AnimationStep   1.000000
END Animation

BEGIN Assets
    Satellite       tehran_daily_pass.sat
    Facility        Facility_Tehran_Urban_Core.fac
    Facility        Facility_Svalbard.fac
    Facility        Facility_Tehran_Iran.fac
END Assets
END Scenario
