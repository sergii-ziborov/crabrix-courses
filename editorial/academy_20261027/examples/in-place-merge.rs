fn csv<T:std::fmt::Display>(a:impl IntoIterator<Item=T>)->String { a.into_iter().map(|x|x.to_string()).collect::<Vec<_>>().join(",") }
fn merge_into(a: &mut [i32], mut m: usize, b: &[i32]) {
    assert_eq!(a.len(),m+b.len()); let mut n=b.len(); let mut write=a.len();
    while n>0 {
        write-=1;
        if m>0 && a[m-1]>b[n-1] { m-=1; a[write]=a[m]; }
        else { n-=1; a[write]=b[n]; }
    }
}

fn main() {
    let result = { let mut a=vec![1,3,7,0,0,0]; merge_into(&mut a,3,&[2,5,6]); csv(a) };
    println!("{result}");
}
