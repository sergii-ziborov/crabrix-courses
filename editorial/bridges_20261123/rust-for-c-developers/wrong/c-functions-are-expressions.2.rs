pub fn is_leap(year: i32) -> bool {
    (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
}

pub fn days_in_february(year: i32) -> u32 {
    if is_leap(year) { 29 } else { 28 }
}
