fn fibonacci_matrix(mut n:u64)->u64 {
    fn multiply(a:[[u64;2];2],b:[[u64;2];2])->[[u64;2];2] {
        let mut out=[[0;2];2]; for i in 0..2 { for j in 0..2 { for k in 0..2 { out[i][j]+=a[i][k]*b[k][j]; } } } out
    }
    assert!(n<=90); let mut result=[[1,0],[0,1]]; let mut power=[[1,1],[1,0]];
    while n>0 { if n&1==1 { result=multiply(result,power); } n>>=1; if n>0 { power=multiply(power,power); } }
    result[0][1]
}

fn main() {
    let result = fibonacci_matrix(50).to_string();
    println!("{result}");
}
