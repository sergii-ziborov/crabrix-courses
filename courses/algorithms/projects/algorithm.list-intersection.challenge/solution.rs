pub fn solve(input: &str) -> String {
    // Input is one of two forms. a_prefix, b_prefix and shared arrays: build separate prefix nodes and attach both to the same shared tail. Or values=[...] next=[...] a=i b=j: an arena of nodes where next holds each node's next index or none, and a and b are the two head indexes. Return the first shared node's value, or none when the lists share no node. Equal values do not identify shared nodes.
    // Parse the visible input into the structures your algorithm needs.
    // Whitespace surrounding the complete input is insignificant.
    let _ = input;
    todo!("implement Pointer-Switch Intersection")
}