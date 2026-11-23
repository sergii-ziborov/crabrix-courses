// C original:
// struct budget { unsigned limit, spent; };
// unsigned budget_remaining(const struct budget *b) { return b->limit - b->spent; }
// int budget_spend(struct budget *b, unsigned amount) {
//     if (b->spent + amount > b->limit) return -1;  /* the sum can wrap */
//     b->spent += amount;
//     return 0;
// }
// unsigned budget_close(struct budget b) { return b.spent; }
pub struct Budget {
    limit: u32,
    spent: u32,
}

impl Budget {
    pub fn new(limit: u32) -> Self {
        todo!("implement the contract")
    }

    pub fn spend(&mut self, amount: u32) -> bool {
        todo!("implement the contract")
    }

    pub fn remaining(&self) -> u32 {
        todo!("implement the contract")
    }

    pub fn close(self) -> u32 {
        todo!("implement the contract")
    }
}
