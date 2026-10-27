fn selection_swaps(values: &mut [i32]) -> usize {
    let mut swaps = 0;
    for i in 0..values.len() {
        let minimum = (i..values.len()).min_by_key(|&j| values[j]).unwrap();
        if minimum != i {
            values.swap(i, minimum);
            swaps += 1;
        }
    }
    swaps // self-swaps are not counted
}

fn main() {
    let result = {
        let mut values = vec![3, 1, 2];
        selection_swaps(&mut values).to_string()
    };
    println!("{result}");
}
