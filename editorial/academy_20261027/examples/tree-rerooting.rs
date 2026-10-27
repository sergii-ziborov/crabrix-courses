fn csv<T:std::fmt::Display>(a:impl IntoIterator<Item=T>)->String { a.into_iter().map(|x|x.to_string()).collect::<Vec<_>>().join(",") }
fn distance_sums(graph:&[Vec<usize>])->Vec<usize> {
    fn collect(v:usize,parent:usize,g:&[Vec<usize>],size:&mut [usize],down:&mut [usize]) {
        size[v]=1;
        for &u in &g[v] { if u!=parent { collect(u,v,g,size,down); size[v]+=size[u]; down[v]+=down[u]+size[u]; } }
    }
    fn reroot(v:usize,parent:usize,g:&[Vec<usize>],size:&[usize],answer:&mut [usize]) {
        for &u in &g[v] { if u!=parent { answer[u]=answer[v]+g.len()-2*size[u]; reroot(u,v,g,size,answer); } }
    }
    let n=graph.len(); if n==0 { return Vec::new(); }
    let (mut size,mut answer)=(vec![0;n],vec![0;n]); collect(0,n,graph,&mut size,&mut answer);
    reroot(0,n,graph,&size,&mut answer); answer
}

fn main() {
    let result = csv(distance_sums(&[vec![1],vec![0,2,3],vec![1],vec![1]]));
    println!("{result}");
}
