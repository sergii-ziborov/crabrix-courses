fn all_pairs(mut distance:Vec<Vec<i64>>)->Vec<Vec<i64>> {
    let n=distance.len(); let infinity=999_999_999;
    for k in 0..n { for i in 0..n { for j in 0..n {
        if distance[i][k]!=infinity && distance[k][j]!=infinity {
            distance[i][j]=distance[i][j].min(distance[i][k]+distance[k][j]);
        }
    } } }
    distance
}

fn main() {
    let result = all_pairs(vec![vec![0,3,10],vec![999999999,0,2],vec![999999999,999999999,0]])[0][2].to_string();
    println!("{result}");
}
