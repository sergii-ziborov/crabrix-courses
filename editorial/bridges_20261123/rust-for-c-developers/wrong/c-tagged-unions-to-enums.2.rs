#[derive(Clone, Copy, Debug, PartialEq)]
pub enum Shape {
    Square { side: u32 },
    Rect { w: u32, h: u32 },
    Triangle { base: u32, height: u32 },
}

pub fn area(shape: &Shape) -> u64 {
    match *shape {
        Shape::Square { side } => u64::from(side) * u64::from(side),
        Shape::Rect { w, h } => u64::from(w) * u64::from(h),
        _ => 0,
    }
}

pub fn is_degenerate(shape: &Shape) -> bool {
    match *shape {
        Shape::Square { side } => side == 0,
        Shape::Rect { w, h } => w == 0 || h == 0,
        Shape::Triangle { base, height } => base == 0 || height == 0,
    }
}
