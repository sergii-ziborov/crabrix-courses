fn main() {
    let markdown = "# Crabrix
Intro text
## Build
### Packages
## Learn
### Practice";

    for line in markdown.lines() {
        let marks = line.chars()
            .take_while(|ch| *ch == '#')
            .count();
        if marks == 0 {
            continue;
        }
        let title = line[marks..].trim();
        println!("{}- {title}", "  ".repeat(marks - 1));
    }
}