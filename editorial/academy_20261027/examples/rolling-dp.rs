fn stair_cost(cost:&[i32])->i32 {
    let (mut two_back,mut one_back)=(0,0);
    for &price in cost { let current=price+two_back.min(one_back); two_back=one_back; one_back=current; }
    two_back.min(one_back)
}

fn main() {
    let result = stair_cost(&[10,15,20]).to_string();
    println!("{result}");
}
