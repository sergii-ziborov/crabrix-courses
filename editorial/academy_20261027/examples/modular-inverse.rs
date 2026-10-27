fn modular_inverse(a:i64,modulus:i64)->Option<i64> {
    assert!(modulus>1); let (mut old_r,mut r)=(a.rem_euclid(modulus),modulus); let (mut old_s,mut s)=(1_i128,0_i128);
    while r!=0 {
        let q=old_r/r; (old_r,r)=(r,old_r-q*r); (old_s,s)=(s,old_s-q as i128*s);
    }
    (old_r==1).then(||old_s.rem_euclid(modulus as i128) as i64)
}

fn main() {
    let result = modular_inverse(3,11).unwrap().to_string();
    println!("{result}");
}
