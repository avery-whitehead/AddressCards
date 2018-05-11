SELECT p.uprn
FROM properties p
    JOIN LLPG_ADDRESS_CURRENT_SPATIAL l
        ON p.uprn = l.uprn
    LEFT JOIN (SELECT * FROM PropertyServiceRounds WHERE serviceid = 'REF' AND RoundEra = 2) psr_ref
        ON p.uprn = psr_ref.uprn
    LEFT JOIN (SELECT * FROM rounds where serviceid = 'REF' AND RoundEra=2) ref
        ON psr_ref.RoundID = ref.RoundID
    LEFT JOIN (SELECT * FROM PropertyServiceRounds WHERE serviceid = 'RECY' AND RoundEra = 2) psr_recy
        ON p.uprn = psr_recy.uprn
    LEFT JOIN (SELECT * FROM rounds WHERE serviceid = 'RECY' and RoundEra = 2) recy
        ON psr_recy.RoundID = recy.RoundID
    LEFT JOIN (SELECT * FROM PropertyServiceRounds WHERE serviceid = 'GW' AND RoundEra = 2) psr_gw
        ON p.uprn = psr_gw.uprn
    LEFT JOIN (SELECT * FROM rounds WHERE serviceid = 'GW' AND RoundEra = 2) gw
        ON psr_gw.RoundID = gw.RoundID
    LEFT JOIN (SELECT * FROM PropertyServiceRounds WHERE serviceid = 'MIX' AND RoundEra = 2) psr_mix
        ON p.uprn = psr_mix.uprn
    LEFT JOIN (SELECT * FROM rounds WHERE serviceid = 'MIX' and RoundEra = 2) mix
        ON psr_mix.RoundID = mix.RoundID
    LEFT JOIN (SELECT * FROM PropertyServiceRounds WHERE serviceid = 'GLASS' AND RoundEra = 2) psr_glass
        ON p.uprn = psr_glass.uprn
    LEFT JOIN (SELECT * FROM rounds WHERE serviceid = 'GLASS' and RoundEra = 2) glass
        ON psr_glass.RoundID = glass.RoundID
WHERE psr_ref.RoundEra = 2
AND mix.ScheduleDayID IS NULL
AND glass.ScheduleDayID IS NULL
