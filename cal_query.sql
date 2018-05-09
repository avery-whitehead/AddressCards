select
       p.uprn
       ,replace(replace(l.ADDRESS_BLOCK_ORG,'North Yorkshire'+char(13)+char(10),''),char(13)+char(10),'<br>') as addressBlock
       ,case
              when ref.ScheduleDayID < 8 then 0
              when ref.ScheduleDayID > 7 then 1
       end as REFWeek
       ,case
              when ref.ScheduleDayID in (1,8) then 'Monday'
              when ref.ScheduleDayID in (2,9) then 'Tuesday'
              when ref.ScheduleDayID in (3,10) then 'Wednesday'
              when ref.ScheduleDayID in (4,11) then 'Thursday'
              when ref.ScheduleDayID in (5,12) then 'Friday'
       end as REFDay
       ,case
              when recy.ScheduleDayID < 8 then 0
              when recy.ScheduleDayID > 7 then 1
       end as RECYWeek
       ,case
              when recy.ScheduleDayID in (1,8) then 'Monday'
              when recy.ScheduleDayID in (2,9) then 'Tuesday'
              when recy.ScheduleDayID in (3,10) then 'Wednesday'
              when recy.ScheduleDayID in (4,11) then 'Thursday'
              when recy.ScheduleDayID in (5,12) then 'Friday'
       end as RECYDay
       ,case
              when gw.ScheduleDayID < 8 then 0
              when gw.ScheduleDayID > 7 then 1
       end as GWWeek
       ,case
              when gw.ScheduleDayID in (1,8) then 'Monday'
              when gw.ScheduleDayID in (2,9) then 'Tuesday'
              when gw.ScheduleDayID in (3,10) then 'Wednesday'
              when gw.ScheduleDayID in (4,11) then 'Thursday'
              when gw.ScheduleDayID in (5,12) then 'Friday'
       end as GWDay
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
where psr_ref.RoundEra=2 and p.uprn in (?)
