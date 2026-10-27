fn csv<T: std::fmt::Display>(a: impl IntoIterator<Item = T>) -> String {
    a.into_iter()
        .map(|x| x.to_string())
        .collect::<Vec<_>>()
        .join(",")
}
fn distinct_queries(values: &[i32], queries: &[(usize, usize)]) -> Vec<usize> {
    let block = (values.len() as f64).sqrt().max(1.0) as usize;
    let mut order: Vec<_> = (0..queries.len()).collect();
    order.sort_by_key(|&i| {
        let (l, r) = queries[i];
        (
            l / block,
            if l / block % 2 == 0 {
                r as isize
            } else {
                -(r as isize)
            },
        )
    });
    let mut counts = std::collections::HashMap::<i32, usize>::new();
    let (mut left, mut right, mut distinct) = (0, 0, 0);
    let mut out = vec![0; queries.len()];
    fn change(
        counts: &mut std::collections::HashMap<i32, usize>,
        distinct: &mut usize,
        x: i32,
        add: bool,
    ) {
        let count = counts.entry(x).or_default();
        if add {
            if *count == 0 {
                *distinct += 1;
            }
            *count += 1;
        } else {
            *count -= 1;
            if *count == 0 {
                *distinct -= 1;
            }
        }
    }
    for i in order {
        let (l, r) = queries[i];
        let end = r + 1;
        while left > l {
            left -= 1;
            change(&mut counts, &mut distinct, values[left], true);
        }
        while right < end {
            change(&mut counts, &mut distinct, values[right], true);
            right += 1;
        }
        while left < l {
            change(&mut counts, &mut distinct, values[left], false);
            left += 1;
        }
        while right > end {
            right -= 1;
            change(&mut counts, &mut distinct, values[right], false);
        }
        out[i] = distinct;
    }
    out
}

fn main() {
    let result = csv(distinct_queries(
        &[1, 2, 1, 3, 2, 4],
        &[(0, 3), (2, 5), (0, 5)],
    ));
    println!("{result}");
}
