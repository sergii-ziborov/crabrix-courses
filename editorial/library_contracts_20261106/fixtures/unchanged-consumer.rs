extern crate retry_policy;
fn main() {
    assert!(retry_policy::RetryPolicy::new(0).is_none());
    for n in [1u8, 3, 255] {
        assert_eq!(retry_policy::RetryPolicy::new(n).unwrap().attempts(), n);
    }
    println!("unchanged consumer passed");
}
