select * from watch m1,watch m2 
inner join sessions s1 on s1.sid = m1.sid
inner join sessions s2 on s2.sid = m2.sid
inner join movies mv1 on m1.mid = mv1.mid
inner join movies mv2 on m2.mid = mv2.mid
where m1.mid<>m2.mid and m1.cid=m2.cid and s1.sdate<s2.sdate
and (mv1.runtime)/2<=m1.duration and (mv2.runtime)/2<=m2.duration
group by m1.mid,m2.mid,strftime('%Y',s2.sdate)
order by count(*),s2.sdate desc;


select * from watch m1,watch m2 
inner join sessions s1 on s1.sid = m1.sid
inner join sessions s2 on s2.sid = m2.sid
inner join movies mv1 on m1.mid = mv1.mid
inner join movies mv2 on m2.mid = mv2.mid
where m1.mid<>m2.mid and m1.cid=m2.cid and s1.sdate<s2.sdate
and (mv1.runtime)/2<=m1.duration and (mv2.runtime)/2<=m2.duration
group by m1.mid,m2.mid,strftime('%m',s2.sdate)
order by count(*),s2.sdate desc;



select * from watch m1,watch m2 
inner join sessions s1 on s1.sid = m1.sid
inner join sessions s2 on s2.sid = m2.sid
inner join movies mv1 on m1.mid = mv1.mid
inner join movies mv2 on m2.mid = mv2.mid
where m1.mid<>m2.mid and m1.cid=m2.cid and s1.sdate<s2.sdate
and (mv1.runtime)/2<=m1.duration and (mv2.runtime)/2<=m2.duration
group by m1.mid,m2.mid
order by count(*),s2.sdate desc;