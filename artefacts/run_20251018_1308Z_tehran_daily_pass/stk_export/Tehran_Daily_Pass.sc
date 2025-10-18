stk.v.11.0
BEGIN Scenario
Name Tehran_Daily_Pass
CentralBody Earth
BEGIN TimePeriod
   StartTime 21 Mar 2026 09:32:00.000
   StopTime 28 Mar 2026 00:00:00.000
END TimePeriod
BEGIN AnalysisTimePeriod
   StartTime 21 Mar 2026 09:32:00.000
   StopTime 28 Mar 2026 00:00:00.000
END AnalysisTimePeriod
BEGIN Animation
   StartTime 21 Mar 2026 09:32:00.000
   StopTime 28 Mar 2026 00:00:00.000
   AnimationStep 1.000
END Animation
BEGIN Assets
   Satellite tehran_daily_pass.sat
   Facility Facility_Tehran_Urban_Core.fac
   Facility Facility_Svalbard.fac
   Facility Facility_Tehran_Iran.fac
END Assets
END Scenario
