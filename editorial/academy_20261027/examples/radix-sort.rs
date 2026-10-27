fn csv<T:std::fmt::Display>(a:impl IntoIterator<Item=T>)->String { a.into_iter().map(|x|x.to_string()).collect::<Vec<_>>().join(",") }
fn radix_sort(values:&mut [u32]) {
    let mut out=vec![0;values.len()];
    for shift in [0,8,16,24] {
        let mut counts=[0;256];
        for &x in values.iter() { counts[((x>>shift)&255) as usize]+=1; }
        let mut total=0; for count in &mut counts { let n=*count; *count=total; total+=n; }
        for &x in values.iter() { let key=((x>>shift)&255) as usize; out[counts[key]]=x; counts[key]+=1; }
        values.copy_from_slice(&out);
    }
}

fn main() {
    let result = { let mut values=vec![170,45,75,90,802,24,2,66]; radix_sort(&mut values); csv(values) };
    println!("{result}");
}
