fn subset_exists(values:&[i32],target:i32)->bool {
    fn sums(a:&[i32])->Vec<i32> {
        let mut out=vec![0]; for &x in a { let n=out.len(); for i in 0..n { out.push(out[i]+x); } } out
    }
    let mid=values.len()/2; let left=sums(&values[..mid]); let mut right=sums(&values[mid..]); right.sort_unstable();
    left.into_iter().any(|x|right.binary_search(&(target-x)).is_ok())
}

fn main() {
    let result = subset_exists(&[7,3,2,9,5,11],15).to_string();
    println!("{result}");
}
