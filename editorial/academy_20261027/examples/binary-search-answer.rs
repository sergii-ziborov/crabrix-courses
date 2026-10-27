fn shipping_capacity(weights:&[i32],days:usize)->i32 {
    assert!(!weights.is_empty() && days>0);
    let (mut lo,mut hi)=(*weights.iter().max().unwrap(),weights.iter().sum());
    while lo<hi {
        let mid=lo+(hi-lo)/2; let (mut used,mut load)=(1,0);
        for &x in weights { if load+x>mid { used+=1; load=0; } load+=x; }
        if used<=days { hi=mid; } else { lo=mid+1; }
    }
    lo
}

fn main() {
    let result = shipping_capacity(&[1,2,3,4,5,6,7,8,9,10],3).to_string();
    println!("{result}");
}
