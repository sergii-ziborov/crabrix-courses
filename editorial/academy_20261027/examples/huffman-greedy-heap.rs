fn merge_cost(weights:&[i64])->i64 {
    let mut heap:std::collections::BinaryHeap<_>=weights.iter().map(|&x|std::cmp::Reverse(x)).collect(); let mut cost=0;
    while heap.len()>1 {
        let merged=heap.pop().unwrap().0+heap.pop().unwrap().0; cost+=merged; heap.push(std::cmp::Reverse(merged));
    }
    cost
}

fn main() {
    let result = merge_cost(&[5,9,12,13,16,45]).to_string();
    println!("{result}");
}
