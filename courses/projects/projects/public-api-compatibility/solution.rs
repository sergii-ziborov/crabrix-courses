pub struct RetryPolicy { attempts: u8, delay_ms: u32 }
impl RetryPolicy {
    pub fn new(attempts: u8) -> Option<Self> { todo!("implement the contract") }
    pub fn attempts(&self) -> u8 { todo!("implement the contract") }
    pub fn delay_ms(&self) -> u32 { todo!("implement the contract") }
    pub fn with_delay(self, delay_ms: u32) -> Self { todo!("implement the contract") }
}
