fn first_last(a:&[i32],target:i32)->(i32,i32) {
    let bound=|upper:bool| {
        let (mut lo,mut hi)=(0,a.len());
        while lo<hi { let mid=lo+(hi-lo)/2; if a[mid]<target || (upper && a[mid]==target) { lo=mid+1; } else { hi=mid; } }
        lo
    };
    let first=bound(false);
    if a.get(first)!=Some(&target) { (-1,-1) } else { (first as i32,bound(true) as i32-1) }
}

fn main() {
    let result = { let (a,b)=first_last(&[5,7,7,8,8,10],8); format!("{a},{b}") };
    println!("{result}");
}
