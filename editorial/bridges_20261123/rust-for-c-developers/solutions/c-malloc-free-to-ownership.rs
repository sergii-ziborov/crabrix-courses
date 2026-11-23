pub fn take_largest(buffers: Vec<Vec<u8>>) -> Option<Vec<u8>> {
    let mut best: Option<Vec<u8>> = None;
    for buffer in buffers {
        let longer = match &best {
            Some(current) => buffer.len() > current.len(),
            None => true,
        };
        if longer {
            best = Some(buffer); // the previous best is dropped here
        }
    }
    best
}
