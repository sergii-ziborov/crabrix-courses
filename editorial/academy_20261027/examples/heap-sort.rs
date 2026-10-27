fn csv<T: std::fmt::Display>(a: impl IntoIterator<Item = T>) -> String {
    a.into_iter()
        .map(|x| x.to_string())
        .collect::<Vec<_>>()
        .join(",")
}
fn heap_sort(a: &mut [i32]) {
    fn sift(a: &mut [i32], mut root: usize, end: usize) {
        while 2 * root + 1 < end {
            let mut child = 2 * root + 1;
            if child + 1 < end && a[child] < a[child + 1] {
                child += 1;
            }
            if a[root] >= a[child] {
                break;
            }
            a.swap(root, child);
            root = child;
        }
    }
    let n = a.len();
    for i in (0..n / 2).rev() {
        sift(a, i, n);
    }
    for end in (1..n).rev() {
        a.swap(0, end);
        sift(a, 0, end);
    }
}

fn main() {
    let result = {
        let mut values = vec![4, 10, 3, 5, 1];
        heap_sort(&mut values);
        csv(values)
    };
    println!("{result}");
}
