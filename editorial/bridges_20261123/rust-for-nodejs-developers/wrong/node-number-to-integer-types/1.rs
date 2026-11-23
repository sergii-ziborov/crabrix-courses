pub fn seats_left(capacity: u32, booked: u32, requested: u32) -> Option<u32> {
    Some(capacity - booked - requested)
}
