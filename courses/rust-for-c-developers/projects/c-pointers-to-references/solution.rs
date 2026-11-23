// C original:
// /* Appends 2 * src[i] to dst. With src == dst->data this reads freed memory
//    as soon as push() reallocates. */
// void append_doubled(struct ivec *dst, const int *src, size_t n) {
//     for (size_t i = 0; i < n; i++) push(dst, 2 * src[i]);
// }
pub fn append_doubled(dst: &mut Vec<i32>, src: &[i32]) {
    todo!("implement the contract")
}
