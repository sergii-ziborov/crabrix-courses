fn stable_merge_sort(values:&[(i32,char)])->Vec<(i32,char)> {
    if values.len()<2 { return values.to_vec(); }
    let mid=values.len()/2; let left=stable_merge_sort(&values[..mid]); let right=stable_merge_sort(&values[mid..]);
    let (mut i,mut j)=(0,0); let mut out=Vec::with_capacity(values.len());
    while i<left.len() && j<right.len() {
        if left[i].0<=right[j].0 { out.push(left[i]); i+=1; } else { out.push(right[j]); j+=1; }
    }
    out.extend_from_slice(&left[i..]); out.extend_from_slice(&right[j..]); out
}

fn main() {
    let result = stable_merge_sort(&[(2,'a'),(1,'x'),(2,'b'),(1,'y')]).iter().map(|(k,v)|format!("{k}{v}")).collect::<Vec<_>>().join(",");
    println!("{result}");
}
