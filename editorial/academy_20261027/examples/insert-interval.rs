fn inserted_interval(intervals:&[(i32,i32)],mut new:(i32,i32))->Vec<(i32,i32)> {
    let mut out=Vec::new(); let mut i=0;
    while i<intervals.len() && intervals[i].1<new.0 { out.push(intervals[i]); i+=1; }
    while i<intervals.len() && intervals[i].0<=new.1 { new.0=new.0.min(intervals[i].0); new.1=new.1.max(intervals[i].1); i+=1; }
    out.push(new); out.extend_from_slice(&intervals[i..]); out
}

fn main() {
    let result = inserted_interval(&[(1,2),(3,5),(6,7),(8,10),(12,16)],(4,8)).iter().map(|(a,b)|format!("{a}-{b}")).collect::<Vec<_>>().join(",");
    println!("{result}");
}
