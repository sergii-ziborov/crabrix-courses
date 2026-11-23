pub struct Wallet {
    cents: u64,
}

impl Wallet {
    pub fn new() -> Wallet {
        Wallet { cents: 0 }
    }

    pub fn deposit(&mut self, amount: u64) {
        self.cents += amount;
    }

    pub fn withdraw(&mut self, amount: u64) -> bool {
        if amount >= self.cents {
            return false;
        }
        self.cents -= amount;
        true
    }

    pub fn balance(&self) -> u64 {
        self.cents
    }

    pub fn close(self) -> u64 {
        self.cents
    }
}
