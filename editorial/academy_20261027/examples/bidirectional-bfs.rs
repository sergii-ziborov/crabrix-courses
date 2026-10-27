fn ladder_length(start:&str,goal:&str,words:&[&str])->usize {
    use std::collections::{HashMap,HashSet};
    let mut front=HashSet::from([start.to_owned()]); let mut back=HashSet::from([goal.to_owned()]);
    let mut left=HashMap::from([(start.to_owned(),1)]); let mut right=HashMap::from([(goal.to_owned(),1)]);
    while !front.is_empty() && !back.is_empty() {
        if front.len()>back.len() { std::mem::swap(&mut front,&mut back); std::mem::swap(&mut left,&mut right); }
        let mut next=HashSet::new(); let mut best=usize::MAX;
        for word in &front {
            if let Some(&d)=right.get(word) { best=best.min(left[word]+d-1); }
            for &candidate in words {
                if candidate.len()!=word.len() || word.bytes().zip(candidate.bytes()).filter(|(a,b)|a!=b).count()!=1 { continue; }
                let d=left[word]+1;
                if let Some(&other)=right.get(candidate) { best=best.min(d+other-1); }
                if !left.contains_key(candidate) { left.insert(candidate.to_owned(),d); next.insert(candidate.to_owned()); }
            }
        }
        if best!=usize::MAX { return best; } front=next;
    }
    0
}

fn main() {
    let result = ladder_length("hit","cog",&["hot","dot","dog","lot","log","cog"]).to_string();
    println!("{result}");
}
