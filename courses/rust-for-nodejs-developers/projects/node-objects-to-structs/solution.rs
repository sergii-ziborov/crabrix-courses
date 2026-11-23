// JavaScript original:
// class Wallet {
//   constructor() { this.cents = 0; }
//   deposit(amount) { this.cents += amount; }
//   withdraw(amount) {
//     if (amount > this.cents) return false;
//     this.cents -= amount;
//     return true;
//   }
//   balance() { return this.cents; }
//   close() { return this.cents; }  // the wallet must not be used afterwards
// }
pub struct Wallet {
    cents: u64,
}

impl Wallet {
    pub fn new() -> Wallet {
        todo!("implement the contract")
    }

    pub fn deposit(&mut self, amount: u64) {
        todo!("implement the contract")
    }

    pub fn withdraw(&mut self, amount: u64) -> bool {
        todo!("implement the contract")
    }

    pub fn balance(&self) -> u64 {
        todo!("implement the contract")
    }

    pub fn close(self) -> u64 {
        todo!("implement the contract")
    }
}
