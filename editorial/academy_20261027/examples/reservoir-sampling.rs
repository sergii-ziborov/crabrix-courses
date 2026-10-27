fn reservoir(values: &[i32], choices: &[usize]) -> Option<i32> {
    assert_eq!(values.len(), choices.len());
    let mut selected = None;
    for (i, (&value, &choice)) in values.iter().zip(choices).enumerate() {
        assert!(choice <= i); // choice is uniform in 0..=i in a random run
        if choice == i {
            selected = Some(value);
        }
    }
    selected
}

fn main() {
    let result =
        reservoir(&[10, 20, 30, 40], &[0, 1, 1, 3]).map_or("none".into(), |x| x.to_string());
    println!("{result}");
}
