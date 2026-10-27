fn exactly_k(values: &[i32], k: usize) -> usize {
    fn at_most(a: &[i32], k: usize) -> usize {
        let mut counts=std::collections::HashMap::new(); let (mut left,mut total)=(0,0);
        for (right,&x) in a.iter().enumerate() {
            *counts.entry(x).or_insert(0)+=1;
            while counts.len()>k {
                let count=counts.get_mut(&a[left]).unwrap(); *count-=1;
                if *count==0 { counts.remove(&a[left]); } left+=1;
            }
            total+=right+1-left;
        }
        total
    }
    if k==0 { 0 } else { at_most(values,k)-at_most(values,k-1) }
}

fn main() {
    let result = exactly_k(&[1,2,1,2,3],2).to_string();
    println!("{result}");
}
