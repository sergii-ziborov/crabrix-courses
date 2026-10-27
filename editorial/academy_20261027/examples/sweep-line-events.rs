fn maximum_sessions(intervals:&[(i32,i32)])->i32 {
    let mut events=Vec::new();
    for &(start,end) in intervals { assert!(start<end); events.push((start,1)); events.push((end,-1)); }
    events.sort_unstable(); // -1 precedes +1: half-open intervals
    let (mut active,mut peak)=(0,0); for (_,delta) in events { active+=delta; peak=peak.max(active); } peak
}

fn main() {
    let result = maximum_sessions(&[(1,4),(2,5),(4,6)]).to_string();
    println!("{result}");
}
