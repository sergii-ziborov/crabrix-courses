pub fn solve(input: &str) -> String {
    // Parse digits in 0..9; leading zeros are allowed. Keep a window of the last three digits, or fewer before three have arrived. Maintain hash=(hash*10+digit)%101 for the window, removing the outgoing digit's contribution, and return the final window's hash.
    // Parse the visible input into the structures your algorithm needs.
    // Whitespace surrounding the complete input is insignificant.
    let _ = input;
    todo!("implement Rolling Fingerprint")
}