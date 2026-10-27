fn csv<T:std::fmt::Display>(a:impl IntoIterator<Item=T>)->String { a.into_iter().map(|x|x.to_string()).collect::<Vec<_>>().join(",") }
fn window_maxima(values: &[i32], k: usize) -> Vec<i32> {
    assert!(k>0 && k<=values.len());
    let mut deque=std::collections::VecDeque::new(); let mut result=Vec::new();
    for (i,&x) in values.iter().enumerate() {
        while deque.front().is_some_and(|&j|j+k<=i) { deque.pop_front(); }
        while deque.back().is_some_and(|&j|values[j]<=x) { deque.pop_back(); }
        deque.push_back(i);
        if i+1>=k { result.push(values[*deque.front().unwrap()]); }
    }
    result
}

fn main() {
    let result = csv(window_maxima(&[1,3,-1,-3,5,3,6,7],3));
    println!("{result}");
}
