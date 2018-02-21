select
       p.uprn
       ,replace(replace(l.ADDRESS_BLOCK_ORG,'North Yorkshire'+char(13)+char(10),''),char(13)+char(10),'<br>') as addressBlock
       ,case
              when ref.ScheduleDayID < 8 then 'Week 1'
              when ref.ScheduleDayID > 7 then 'Week 2'
              else ' '
       end as REFWeek
       ,case
              when ref.ScheduleDayID in (1,8) then 'Mon'
              when ref.ScheduleDayID in (2,9) then 'Tue'
              when ref.ScheduleDayID in (3,10) then 'Wed'
              when ref.ScheduleDayID in (4,11) then 'Thu'
              when ref.ScheduleDayID in (5,12) then 'Fri'
              else '-'
       end as REFDay
       ,case
              when recy.ScheduleDayID < 8 then 'Week 1'
              when recy.ScheduleDayID > 7 then 'Week 2'
              else ' '
       end as RECYWeek
       ,case
              when recy.ScheduleDayID in (1,8) then 'Mon'
              when recy.ScheduleDayID in (2,9) then 'Tue'
              when recy.ScheduleDayID in (3,10) then 'Wed'
              when recy.ScheduleDayID in (4,11) then 'Thu'
              when recy.ScheduleDayID in (5,12) then 'Fri'
              else '-'
       end as RECYDay
       ,case
              when gw.ScheduleDayID < 8 then 'Week 1'
              when gw.ScheduleDayID > 7 then 'Week 2'
              else ' '
       end as GWWeek
       ,case
              when gw.ScheduleDayID in (1,8) then 'Mon'
              when gw.ScheduleDayID in (2,9) then 'Tue'
              when gw.ScheduleDayID in (3,10) then 'Wed'
              when gw.ScheduleDayID in (4,11) then 'Thu'
              when gw.ScheduleDayID in (5,12) then 'Fri'
              else '-'
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
