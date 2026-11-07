use std::io::{self, Read};

// This safe wrapper is the sole local database host boundary. Desktop SQLx has
// its own driver; this module does not pretend that SQLite is a WASI syscall.
fn quote(value: &str) -> String {
    let mut result = String::from("\"");
    for c in value.chars() {
        match c {
            '"' => result.push_str("\\\""),
            '\\' => result.push_str("\\\\"),
            '\n' => result.push_str("\\n"),
            '\r' => result.push_str("\\r"),
            '\t' => result.push_str("\\t"),
            c if c < ' ' => result.push_str(&format!("\\u{:04x}", c as u32)),
            c => result.push(c),
        }
    }
    result.push('"');
    result
}
fn json_text(input: &str) -> Option<String> {
    let mut chars = input.chars();
    if chars.next()? != '"' {
        return None;
    }
    let mut output = String::new();
    while let Some(c) = chars.next() {
        match c {
            '"' => {
                return if chars.next().is_none() {
                    Some(output)
                } else {
                    None
                };
            }
            '\\' => match chars.next()? {
                '"' => output.push('"'),
                '\\' => output.push('\\'),
                '/' => output.push('/'),
                'n' => output.push('\n'),
                'r' => output.push('\r'),
                't' => output.push('\t'),
                'b' => output.push('\u{8}'),
                'f' => output.push('\u{c}'),
                'u' => {
                    let mut value = 0u32;
                    for _ in 0..4 {
                        value = value * 16 + chars.next()?.to_digit(16)?;
                    }
                    if (0xd800..=0xdbff).contains(&value) {
                        if chars.next()? != '\\' || chars.next()? != 'u' {
                            return None;
                        }
                        let mut low = 0u32;
                        for _ in 0..4 {
                            low = low * 16 + chars.next()?.to_digit(16)?;
                        }
                        if !(0xdc00..=0xdfff).contains(&low) {
                            return None;
                        }
                        value = 0x10000 + ((value - 0xd800) << 10) + low - 0xdc00;
                    }
                    output.push(char::from_u32(value)?);
                }
                _ => return None,
            },
            c if c < ' ' => return None,
            c => output.push(c),
        }
    }
    None
}
fn query(sql: &str, params: &[&str]) -> Result<String, String> {
    let request = format!(
        "{{\"sql\":{},\"params\":[{}],\"jsonResult\":true}}",
        quote(sql),
        params
            .iter()
            .map(|p| quote(p))
            .collect::<Vec<_>>()
            .join(",")
    );
    #[cfg(target_arch = "wasm32")]
    {
        #[link(wasm_import_module = "crabrix_sql")]
        unsafe extern "C" {
            #[link_name = "crabrix_sql_query"]
            fn crabrix_sql_query(p: *const u8, n: usize, out: *mut u8, capacity: usize) -> i32;
        }
        let mut out = vec![0u8; 65536];
        // Both buffers remain allocated for the synchronous bounded host call.
        let size = unsafe {
            crabrix_sql_query(request.as_ptr(), request.len(), out.as_mut_ptr(), out.len())
        };
        if size < 0 || size as usize > out.len() {
            return Err("database response exceeds the local limit".into());
        }
        out.truncate(size as usize);
        let result = String::from_utf8(out).map_err(|_| "database returned invalid UTF-8")?;
        if result.starts_with("{\"error\":") {
            Err(result)
        } else {
            Ok(result)
        }
    }
    #[cfg(not(target_arch = "wasm32"))]
    {
        let _ = request;
        Err("Use the local Crabrix SQL host or the desktop SQLx companion".into())
    }
}
fn response(status: u16, body: &str, request_id: &str) -> String {
    let reason = match status {
        200 => "OK",
        201 => "Created",
        400 => "Bad Request",
        404 => "Not Found",
        405 => "Method Not Allowed",
        409 => "Conflict",
        _ => "Internal Server Error",
    };
    format!(
        "HTTP/1.1 {status} {reason}\r\nContent-Type: application/json\r\nX-Request-ID: {request_id}\r\nContent-Length: {}\r\n\r\n{body}",
        body.len()
    )
}
fn handle(input: &str) -> String {
    let Some((headers, body)) = input.split_once("\r\n\r\n") else {
        return response(400, "{\"error\":\"framing\"}", "local");
    };
    let mut lines = headers.split("\r\n");
    let first: Vec<_> = lines.next().unwrap_or("").split_whitespace().collect();
    if first.len() != 3 {
        return response(400, "{\"error\":\"request line\"}", "local");
    }
    let mut request_id = "local";
    let mut key = None;
    let mut content_type = None;
    for line in lines {
        if let Some((name, value)) = line.split_once(':') {
            let value = value.trim();
            if name.eq_ignore_ascii_case("x-request-id")
                && !value.is_empty()
                && value.len() <= 64
                && value
                    .bytes()
                    .all(|b| b.is_ascii_alphanumeric() || b == b'-' || b == b'_')
            {
                request_id = value;
            }
            if name.eq_ignore_ascii_case("content-type") {
                content_type = Some(value);
            }
            if name.eq_ignore_ascii_case("idempotency-key") {
                key = Some(value);
            }
        }
    }
    let path = first[1].split('?').next().unwrap_or("");
    match (first[0], path) {
        ("GET", "/health") => response(200, "{\"ok\":true}", request_id),
        ("GET", "/tasks") => match query(
            "SELECT json_group_array(json_object('id',id,'title',title,'done',json(CASE done WHEN 1 THEN 'true' ELSE 'false' END))) FROM (SELECT * FROM tasks ORDER BY id)",
            &[],
        ) {
            Ok(value) => response(200, &value, request_id),
            Err(_) => response(
                500,
                "{\"error\":\"database schema unavailable\"}",
                request_id,
            ),
        },
        ("POST", "/tasks") => {
            if !content_type.is_some_and(|value: &str| {
                value
                    .split(';')
                    .next()
                    .unwrap_or("")
                    .trim()
                    .eq_ignore_ascii_case("application/json")
            }) {
                return response(
                    415,
                    "{\"error\":\"JSON content type required\"}",
                    request_id,
                );
            }
            let Some(key) = key.filter(|k| {
                !k.is_empty()
                    && k.len() <= 64
                    && k.bytes()
                        .all(|b| b.is_ascii_alphanumeric() || b == b'-' || b == b'_')
            }) else {
                return response(400, "{\"error\":\"idempotency key required\"}", request_id);
            };
            let extracted = query(
                "SELECT CASE WHEN json_valid(?1) THEN CASE WHEN json_type(?1,'$.title')='text' THEN json_quote(json_extract(?1,'$.title')) ELSE 'null' END ELSE 'null' END",
                &[body],
            );
            let title = extracted
                .ok()
                .and_then(|value| json_text(&value))
                .map(|value| value.trim().to_owned());
            let Some(title) =
                title.filter(|value| !value.is_empty() && value.chars().count() <= 80)
            else {
                return response(400, "{\"error\":\"invalid title\"}", request_id);
            };
            match query(
                "SELECT json_object('count',count(*),'same',coalesce(max(title=?1),0)) FROM tasks WHERE request_key=?2",
                &[&title, key],
            ) {
                Ok(value) if value == "{\"count\":1,\"same\":0}" => {
                    return response(409, "{\"error\":\"idempotency conflict\"}", request_id);
                }
                Ok(value) if value == "{\"count\":1,\"same\":1}" => {
                    return match query(
                        "SELECT json_object('id',id,'title',title,'done',json(CASE done WHEN 1 THEN 'true' ELSE 'false' END)) FROM tasks WHERE request_key=?1",
                        &[key],
                    ) {
                        Ok(value) => response(200, &value, request_id),
                        Err(_) => response(500, "{\"error\":\"database\"}", request_id),
                    };
                }
                Err(_) => {
                    return response(
                        500,
                        "{\"error\":\"database schema unavailable\"}",
                        request_id,
                    );
                }
                _ => {}
            }
            match query(
                "INSERT INTO tasks(title,request_key) VALUES(?1,?2) RETURNING json_object('id',id,'title',title,'done',json('false'))",
                &[&title, key],
            ) {
                Ok(value) => response(201, &value, request_id),
                Err(_) => response(500, "{\"error\":\"database write\"}", request_id),
            }
        }
        (_, "/tasks" | "/health") => response(405, "{\"error\":\"method\"}", request_id),
        _ => response(404, "{\"error\":\"route\"}", request_id),
    }
}
fn main() {
    let args: Vec<_> = std::env::args().skip(1).collect();
    if !args.is_empty() {
        match args.as_slice() {
            [command] if command == "list" => {
                let raw = std::env::var("TASK_LIMIT").unwrap_or_else(|_| "20".into());
                let limit: u16 = match raw.parse() {
                    Ok(n) if (1..=100).contains(&n) => n,
                    _ => {
                        eprintln!("error: invalid limit");
                        std::process::exit(2);
                    }
                };
                match query(
                    "SELECT json_group_array(json_object('id',id,'title',title,'done',json(CASE done WHEN 1 THEN 'true' ELSE 'false' END))) FROM (SELECT * FROM tasks ORDER BY id LIMIT ?1)",
                    &[&limit.to_string()],
                ) {
                    Ok(value) => println!("{value}"),
                    Err(error) => {
                        eprintln!("error: {error}");
                        std::process::exit(2);
                    }
                }
            }
            [command, title]
                if command == "add"
                    && !title.trim().is_empty()
                    && title.trim().chars().count() <= 80 =>
            {
                let key = format!(
                    "cli-{}",
                    std::time::SystemTime::now()
                        .duration_since(std::time::UNIX_EPOCH)
                        .unwrap()
                        .as_nanos()
                );
                match query(
                    "INSERT INTO tasks(title,request_key) VALUES(?1,?2) RETURNING json_object('id',id,'title',title,'done',json('false'))",
                    &[title.trim(), &key],
                ) {
                    Ok(value) => println!("{value}"),
                    Err(error) => {
                        eprintln!("error: {error}");
                        std::process::exit(2);
                    }
                }
            }
            [command] if command == "import" => {
                let mut text = String::new();
                if io::stdin().take(65537).read_to_string(&mut text).is_err() || text.len() > 65536
                {
                    eprintln!("error: input limit");
                    std::process::exit(2);
                }
                let titles: Vec<_> = text
                    .lines()
                    .map(str::trim)
                    .filter(|s| !s.is_empty())
                    .collect();
                if titles.iter().any(|line| line.chars().count() > 80) {
                    eprintln!("error: title too long");
                    std::process::exit(2);
                }
                for line in titles {
                    println!("{}", quote(line));
                }
            }
            _ => {
                eprintln!("error: usage: list | add TITLE | import");
                std::process::exit(2);
            }
        }
    } else {
        let mut input = String::new();
        if io::stdin().take(65537).read_to_string(&mut input).is_err() || input.len() > 65536 {
            print!("{}", response(400, "{\"error\":\"input limit\"}", "local"));
            return;
        }
        print!("{}", handle(&input));
    }
}
#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn health_and_route() {
        assert!(handle("GET /health HTTP/1.1\r\n\r\n").starts_with("HTTP/1.1 200"));
        assert!(handle("DELETE /tasks HTTP/1.1\r\n\r\n").starts_with("HTTP/1.1 405"));
        assert!(handle("GET /missing HTTP/1.1\r\n\r\n").starts_with("HTTP/1.1 404"));
    }
    #[test]
    fn json_string_is_bounded_data() {
        assert_eq!(quote("🦀\n\""), "\"🦀\\n\\\"\"");
    }
}

#[cfg(test)]
mod json_decode_tests {
    use super::*;
    #[test]
    fn roundtrip_and_surrogate_validation() {
        for value in ["", "🦀", "a\n\"b", "\u{2000}"] {
            assert_eq!(json_text(&quote(value)).as_deref(), Some(value));
        }
        assert_eq!(json_text(r#""\ud83e\udd80""#).as_deref(), Some("🦀"));
        assert!(json_text(r#""\ud800""#).is_none());
        assert!(json_text(r#""x" trailing"#).is_none());
    }
}
