// TypeScript original:
// interface Settings { pageSize?: number; title?: string }
// function pageSize(s?: Settings): number {
//   return s?.pageSize ?? 20;
// }
// function title(s?: Settings): string {
//   return s?.title ?? "Untitled";
// }
pub struct Settings {
    pub page_size: Option<u32>,
    pub title: Option<String>,
}

pub fn page_size(s: Option<&Settings>) -> u32 {
    todo!("implement the contract")
}

pub fn title(s: Option<&Settings>) -> String {
    todo!("implement the contract")
}
