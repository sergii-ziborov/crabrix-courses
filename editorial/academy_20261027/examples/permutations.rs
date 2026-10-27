fn permutation_count(values:&[i32])->usize {
    fn choose(used:&mut [bool],depth:usize)->usize {
        if depth==used.len() { return 1; } let mut total=0;
        for i in 0..used.len() { if !used[i] { used[i]=true; total+=choose(used,depth+1); used[i]=false; } } total
    }
    choose(&mut vec![false;values.len()],0)
}

fn main() {
    let result = permutation_count(&[1,2,3,4]).to_string();
    println!("{result}");
}
