fn csv<T: std::fmt::Display>(a: impl IntoIterator<Item = T>) -> String {
    a.into_iter()
        .map(|x| x.to_string())
        .collect::<Vec<_>>()
        .join(",")
}
fn quicksort(a: &mut [i32]) {
    if a.len() < 2 {
        return;
    }
    let pivot = a[a.len() / 2];
    let (mut low, mut i, mut high) = (0, 0, a.len());
    while i < high {
        if a[i] < pivot {
            a.swap(low, i);
            low += 1;
            i += 1;
        } else if a[i] > pivot {
            high -= 1;
            a.swap(i, high);
        } else {
            i += 1;
        }
    }
    quicksort(&mut a[..low]);
    quicksort(&mut a[high..]);
}

fn main() {
    let result = {
        let mut values = vec![9, 3, 7, 1, 8, 2];
        quicksort(&mut values);
        csv(values)
    };
    println!("{result}");
}
