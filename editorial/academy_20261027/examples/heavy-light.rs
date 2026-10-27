fn heavy_light_sum(graph:&[Vec<usize>],values:&[i64],mut a:usize,mut b:usize)->i64 {
    fn sizes(v:usize,p:usize,g:&[Vec<usize>],parent:&mut [usize],depth:&mut [usize],size:&mut [usize],heavy:&mut [usize]) {
        parent[v]=p; size[v]=1;
        for &u in &g[v] { if u!=p {
            depth[u]=depth[v]+1; sizes(u,v,g,parent,depth,size,heavy); size[v]+=size[u];
            if heavy[v]==g.len() || size[u]>size[heavy[v]] { heavy[v]=u; }
        } }
    }
    fn split(v:usize,h:usize,g:&[Vec<usize>],parent:&[usize],heavy:&[usize],head:&mut [usize],position:&mut [usize],timer:&mut usize) {
        head[v]=h; position[v]=*timer; *timer+=1;
        if heavy[v]!=g.len() { split(heavy[v],h,g,parent,heavy,head,position,timer); }
        for &u in &g[v] { if u!=parent[v] && u!=heavy[v] { split(u,u,g,parent,heavy,head,position,timer); } }
    }
    let n=graph.len(); let (mut parent,mut depth,mut size,mut heavy)=(vec![n;n],vec![0;n],vec![0;n],vec![n;n]);
    sizes(0,n,graph,&mut parent,&mut depth,&mut size,&mut heavy);
    let (mut head,mut position)=(vec![0;n],vec![0;n]); split(0,0,graph,&parent,&heavy,&mut head,&mut position,&mut 0);
    let mut bit=vec![0;n+1];
    for v in 0..n { let mut i=position[v]+1; while i<=n { bit[i]+=values[v]; i+=i&i.wrapping_neg(); } }
    let prefix=|mut i:usize| { let mut sum=0; while i>0 { sum+=bit[i]; i&=i-1; } sum };
    let mut sum=0;
    while head[a]!=head[b] {
        if depth[head[a]]<depth[head[b]] { std::mem::swap(&mut a,&mut b); }
        sum+=prefix(position[a]+1)-prefix(position[head[a]]); a=parent[head[a]];
    }
    let (left,right)=(position[a].min(position[b]),position[a].max(position[b])); sum+prefix(right+1)-prefix(left)
}

fn main() {
    let result = heavy_light_sum(&[vec![1],vec![0,2,3],vec![1],vec![1,4],vec![3]],&[1,2,3,4,5],2,4).to_string();
    println!("{result}");
}
