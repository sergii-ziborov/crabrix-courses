fn winner(board: &[char; 9]) -> Option<char> {
    let lines = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],
        [0, 3, 6], [1, 4, 7], [2, 5, 8],
        [0, 4, 8], [2, 4, 6],
    ];
    for [a, b, c] in lines {
        let mark = board[a];
        if mark != ' '
            && mark == board[b]
            && mark == board[c]
        {
            return Some(mark);
        }
    }
    None
}

fn main() {
    let board = [
        'X', 'O', 'X',
        'O', 'X', ' ',
        'X', ' ', 'O',
    ];
    for row in board.chunks(3) {
        println!("{}|{}|{}", row[0], row[1], row[2]);
    }
    println!("winner: {:?}", winner(&board));
}