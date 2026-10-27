fn exponential_index(a:&[i32],target:i32)->i32 {
    if a.first()==Some(&target) { return 0; }
    let mut bound=1;
    while bound<a.len() && a[bound]<target { bound=bound.saturating_mul(2); }
    let (mut lo,mut hi)=(bound/2,a.len().min(bound.saturating_add(1)));
    while lo<hi { let mid=lo+(hi-lo)/2; if a[mid]<target { lo=mid+1; } else { hi=mid; } }
    if a.get(lo)==Some(&target) { lo as i32 } else { -1 }
}

fn main() {
    let result = exponential_index(&[1,3,5,7,9,12,15,18,21,24],21).to_string();
    println!("{result}");
}
