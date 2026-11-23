// C original:
// enum kind { SQUARE, RECT, TRIANGLE };
// struct shape { enum kind kind; uint32_t a, b; };
// uint64_t area(const struct shape *s) {
//     switch (s->kind) {
//     case SQUARE: return s->a * s->a;          /* 32-bit multiply, then widened */
//     case RECT:   return (uint64_t)s->a * s->b;
//     default:     return 0;                    /* TRIANGLE was forgotten */
//     }
// }
#[derive(Clone, Copy, Debug, PartialEq)]
pub enum Shape {
    Square { side: u32 },
    Rect { w: u32, h: u32 },
    Triangle { base: u32, height: u32 },
}

/// The area, rounded down.
pub fn area(shape: &Shape) -> u64 {
    todo!("implement the contract")
}

/// True when any dimension is zero.
pub fn is_degenerate(shape: &Shape) -> bool {
    todo!("implement the contract")
}
