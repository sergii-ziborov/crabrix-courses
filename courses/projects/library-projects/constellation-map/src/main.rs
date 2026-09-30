const W: usize = 24;
const H: usize = 16;

fn main() {
    let stars = [
        (3, 4, 2), (8, 2, 1), (11, 7, 2),
        (15, 5, 1), (19, 3, 2), (20, 11, 1),
        (6, 12, 2), (13, 13, 1),
    ];
    let mut pixels = vec!['0'; W * H];
    for (x, y, brightness) in stars {
        pixels[y * W + x] = if brightness == 2 {
            '3'
        } else {
            '2'
        };
        if x + 1 < W { pixels[y * W + x + 1] = '1'; }
    }
    let pixels: String = pixels.into_iter().collect();
    println!(
        r##"CRABRIX_CANVAS:{{"title":"Constellation Map","width":24,"height":16,"palette":["#020617","#334155","#93C5FD","#FFFFFF"],"pixels":"{}"}}"##,
        pixels
    );
    println!("Eight stars plotted from tuple data.");
}