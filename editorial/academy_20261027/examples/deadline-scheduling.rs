fn maximum_profit(jobs:&[(usize,i32)])->i32 {
    fn free(parent:&mut [usize],x:usize)->usize {
        if parent[x]!=x { parent[x]=free(parent,parent[x]); } parent[x]
    }
    let mut sorted=jobs.to_vec(); sorted.sort_by_key(|&(d,p)|(std::cmp::Reverse(p),d));
    let n=jobs.len(); let mut parent:Vec<_>=(0..=n).collect(); let mut profit=0;
    for (deadline,value) in sorted {
        if value<=0 { continue; } let slot=free(&mut parent,deadline.min(n));
        if slot>0 { profit+=value; parent[slot]=free(&mut parent,slot-1); }
    } profit
}

fn main() {
    let result = maximum_profit(&[(2,100),(1,19),(2,27),(1,25),(3,15)]).to_string();
    println!("{result}");
}
