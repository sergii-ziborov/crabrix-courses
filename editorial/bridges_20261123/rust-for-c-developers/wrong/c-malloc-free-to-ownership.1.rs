pub fn take_largest(buffers: Vec<Vec<u8>>) -> Option<Vec<u8>> {
    buffers.iter().max_by_key(|buffer| buffer.len()).cloned()
}
