// C original:
// /* Returns the length of the longest run of equal neighbours; *start gets its index. */
// size_t longest_run(const int *xs, size_t n, size_t *start) {
//     size_t best = 0, best_start = 0, run = 0;
//     for (size_t i = 0; i < n; i++) {
//         run = (i > 0 && xs[i] == xs[i - 1]) ? run + 1 : 1;
//         if (run > best) { best = run; best_start = i + 1 - run; }
//     }
//     *start = best_start;
//     return best;
// }
pub fn longest_run(xs: &[i32]) -> &[i32] {
    todo!("implement the contract")
}
