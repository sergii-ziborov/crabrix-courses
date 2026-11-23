// C original:
// /* Returns a translated deep copy; the caller frees result.pts. The input is unchanged. */
// struct path translated(const struct path *p, int dx, int dy) {
//     struct path out = {malloc(p->len * sizeof *p->pts), p->len};
//     for (size_t i = 0; i < p->len; i++)
//         out.pts[i] = (struct point){p->pts[i].x + dx, p->pts[i].y + dy};
//     return out;
// }
// /* Copies the first point into *out; returns 0 when the path is empty. */
// int first_point(const struct path *p, struct point *out);
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Point {
    pub x: i32,
    pub y: i32,
}

#[derive(Clone, Debug, PartialEq)]
pub struct Path {
    pub points: Vec<Point>,
}

pub fn translated(path: &Path, dx: i32, dy: i32) -> Path {
    todo!("implement the contract")
}

pub fn first_point(path: &Path) -> Option<Point> {
    todo!("implement the contract")
}
