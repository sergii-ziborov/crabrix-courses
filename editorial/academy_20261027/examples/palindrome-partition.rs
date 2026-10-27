fn palindrome_partitions(text:&str)->usize {
    assert!(text.is_ascii()); let a=text.as_bytes(); let n=a.len(); let mut palindrome=vec![vec![false;n];n];
    for i in (0..n).rev() { for j in i..n { palindrome[i][j]=a[i]==a[j] && (j-i<2 || palindrome[i+1][j-1]); } }
    fn count(i:usize,p:&[Vec<bool>])->usize {
        if i==p.len() { return 1; } (i..p.len()).filter(|&j|p[i][j]).map(|j|count(j+1,p)).sum()
    }
    count(0,&palindrome)
}

fn main() {
    let result = palindrome_partitions("aab").to_string();
    println!("{result}");
}
