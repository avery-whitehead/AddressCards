select TOP(1000)
       p.uprn
from properties p
       join LLPG_ADDRESS_CURRENT_SPATIAL l
                     on p.uprn=l.uprn
       left join (select * from PropertyServiceRounds where serviceid = 'REF' and RoundEra=2) psr_ref
              on p.uprn=psr_ref.uprn
       left join (select * from rounds where serviceid = 'REF' and RoundEra=2)  ref
              on psr_ref.RoundID=ref.RoundID
       left join (select * from PropertyServiceRounds where serviceid = 'RECY' and RoundEra=2) psr_recy
              on p.uprn=psr_recy.uprn
       left join (select * from rounds where serviceid = 'RECY' and RoundEra=2)  recy
              on psr_recy.RoundID=recy.RoundID
       left join (select * from PropertyServiceRounds where serviceid = 'GW' and RoundEra=2) psr_gw
              on p.uprn=psr_gw.uprn
       left join (select * from rounds where serviceid = 'GW' and RoundEra=2)  gw
              on psr_gw.RoundID=gw.RoundID
       left join (select * from PropertyServiceRounds where serviceid = 'MIX' and RoundEra=2) psr_mix
              on p.uprn=psr_mix.uprn
       left join (select * from rounds where serviceid = 'MIX' and RoundEra=2)  mix
              on psr_mix.RoundID=mix.RoundID
       left join (select * from PropertyServiceRounds where serviceid = 'GLASS' and RoundEra=2) psr_glass
              on p.uprn=psr_glass.uprn
       left join (select * from rounds where serviceid = 'GLASS' and RoundEra=2)  glass
              on psr_glass.RoundID=glass.RoundID
where psr_ref.RoundEra=2
and mix.ScheduleDayID is null and glass.ScheduleDayID is null
