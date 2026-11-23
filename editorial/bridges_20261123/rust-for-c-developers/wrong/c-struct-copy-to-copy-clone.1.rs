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
    let mut out = Path { points: path.points };
    for p in &mut out.points {
        p.x += dx;
        p.y += dy;
    }
    out
}

pub fn first_point(path: &Path) -> Option<Point> {
    path.points.first().copied()
}
