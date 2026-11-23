// JavaScript original:
// function initials(name) {
//   return name.split(" ").filter(Boolean)
//     .map((part) => part[0].toUpperCase()).join("");
// }
// part[0] is one UTF-16 code unit, so it breaks on characters outside the BMP.
pub fn initials(name: &str) -> String {
    todo!("implement the contract")
}
