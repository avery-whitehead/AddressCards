SELECT
    p.uprn,
    REPLACE(REPLACE(l.ADDRESS_BLOCK_ORG, 'North Yorkshire' + CHAR(13) + CHAR(10), ''), CHAR(13) + CHAR(10), '<br>') AS addressBlock,
        CASE
            WHEN ref.ScheduleDayID < 8 then 0
            WHEN ref.ScheduleDayID > 7 then 1
        END
    AS REFWeek,
        CASE
            WHEN ref.ScheduleDayID IN (1, 8) THEN 'Monday'
            WHEN ref.ScheduleDayID IN (2, 9) THEN 'Tuesday'
            WHEN ref.ScheduleDayID IN (3, 10) THEN 'Wednesday'
            WHEN ref.ScheduleDayID IN (4, 11) THEN 'Thursday'
            WHEN ref.ScheduleDayID IN (5, 12) THEN 'Friday'
        END
    AS REFDay,
        CASE
            WHEN recy.ScheduleDayID < 8 THEN 0
            WHEN recy.ScheduleDayID > 7 THEN 1
       END
    AS RECYWeek,
        CASE
            WHEN recy.ScheduleDayID IN (1, 8) THEN 'Monday'
            WHEN recy.ScheduleDayID IN (2, 9) THEN 'Tuesday'
            WHEN recy.ScheduleDayID IN (3, 10) THEN 'Wednesday'
            WHEN recy.ScheduleDayID IN (4, 11) THEN 'Thursday'
            WHEN recy.ScheduleDayID IN (5, 12) THEN 'Friday'
       END
    AS RECYDay,
        CASE
            WHEN gw.ScheduleDayID < 8 THEN 0
            WHEN gw.ScheduleDayID > 7 THEN 1
        END
    AS GWWeek,
        CASE
            WHEN gw.ScheduleDayID IN (1, 8) THEN 'Monday'
            WHEN gw.ScheduleDayID IN (2, 9) THEN 'Tuesday'
            WHEN gw.ScheduleDayID IN (3, 10) THEN 'Wednesday'
            WHEN gw.ScheduleDayID IN (4, 11) THEN 'Thursday'
            WHEN gw.ScheduleDayID IN (5, 12) THEN 'Friday'
       END
    AS GWDay
FROM properties p
    JOIN LLPG_ADDRESS_CURRENT_SPATIAL l
        ON p.uprn = l.uprn
    LEFT JOIN (SELECT * FROM PropertyServiceRounds WHERE serviceid = 'REF' AND RoundEra = 2) psr_ref
        ON p.uprn = psr_ref.uprn
    LEFT JOIN (SELECT * FROM rounds WHERE serviceid = 'REF' AND RoundEra = 2) ref
        ON psr_ref.RoundID = ref.RoundID
    LEFT JOIN (SELECT * FROM PropertyServiceRounds WHERE serviceid = 'RECY' AND RoundEra = 2) psr_recy
        ON p.uprn = psr_recy.uprn
    LEFT JOIN (SELECT * FROM rounds WHERE serviceid = 'RECY' AND RoundEra = 2) recy
        ON psr_recy.RoundID = recy.RoundID
    LEFT JOIN (SELECT * FROM PropertyServiceRounds WHERE serviceid = 'GW' AND RoundEra = 2) psr_gw
        ON p.uprn = psr_gw.uprn
    LEFT JOIN (SELECT * FROM rounds WHERE serviceid = 'GW' AND RoundEra = 2) gw
        ON psr_gw.RoundID = gw.RoundID
WHERE psr_ref.RoundEra = 2
AND p.uprn IN (?)
