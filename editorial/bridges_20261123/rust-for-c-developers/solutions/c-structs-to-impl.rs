pub struct Budget {
    limit: u32,
    spent: u32,
}

impl Budget {
    pub fn new(limit: u32) -> Self {
        Budget { limit, spent: 0 }
    }

    pub fn spend(&mut self, amount: u32) -> bool {
        if amount > self.remaining() {
            return false;
        }
        self.spent += amount;
        true
    }

    pub fn remaining(&self) -> u32 {
        self.limit - self.spent
    }

    pub fn close(self) -> u32 {
        self.spent
    }
}
