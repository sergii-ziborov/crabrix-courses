struct RollbackDsu { parent:Vec<usize>, size:Vec<usize>, history:Vec<(usize,usize,usize)> }
impl RollbackDsu {
    fn new(n:usize)->Self { Self{parent:(0..n).collect(),size:vec![1;n],history:Vec::new()} }
    fn root(&self,mut v:usize)->usize { while v!=self.parent[v] { v=self.parent[v]; } v }
    fn join(&mut self,a:usize,b:usize) {
        let (mut a,mut b)=(self.root(a),self.root(b)); if a==b { return; }
        if self.size[a]<self.size[b] { std::mem::swap(&mut a,&mut b); }
        self.history.push((b,a,self.size[a])); self.parent[b]=a; self.size[a]+=self.size[b];
    }
    fn checkpoint(&self)->usize { self.history.len() }
    fn rollback(&mut self,mark:usize) {
        while self.history.len()>mark { let (b,a,size)=self.history.pop().unwrap(); self.parent[b]=b; self.size[a]=size; }
    }
}
fn rollback_query(n:usize,before:&[(usize,usize)],after:&[(usize,usize)],query:(usize,usize))->bool {
    let mut dsu=RollbackDsu::new(n); for &(a,b) in before { dsu.join(a,b); } let mark=dsu.checkpoint();
    for &(a,b) in after { dsu.join(a,b); } dsu.rollback(mark); dsu.root(query.0)==dsu.root(query.1)
}

fn main() {
    let result = rollback_query(4,&[(0,1),(1,2)],&[(2,3)],(0,3)).to_string();
    println!("{result}");
}
