fn quickselect(a: &mut [i32], k: usize) -> i32 {
    assert!(k < a.len());
    let pivot = a[a.len() / 2];
    let (mut low, mut i, mut high) = (0, 0, a.len());
    while i < high {
        if a[i] < pivot {
            a.swap(i, low);
            low += 1;
            i += 1;
        } else if a[i] > pivot {
            high -= 1;
            a.swap(i, high);
        } else {
            i += 1;
        }
    }
    if k < low {
        quickselect(&mut a[..low], k)
    } else if k >= high {
        quickselect(&mut a[high..], k - high)
    } else {
        pivot
    }
}

fn main() {
    let result = {
        let mut a = vec![7, 10, 4, 3, 20, 15];
        quickselect(&mut a, 2).to_string()
    };
    println!("{result}");
}
