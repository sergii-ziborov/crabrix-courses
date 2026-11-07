use axum::{
    Json, Router,
    extract::{DefaultBodyLimit, State},
    http::{HeaderMap, StatusCode},
    response::IntoResponse,
    routing::get,
};
use serde_json::{Value, json};
use sqlx::{
    Row, SqlitePool,
    sqlite::{SqliteConnectOptions, SqlitePoolOptions},
};
use std::{str::FromStr, time::Duration};

fn task(row: &sqlx::sqlite::SqliteRow) -> Value {
    json!({"id":row.get::<i64,_>("id"),"title":row.get::<String,_>("title"),"done":row.get::<i64,_>("done")!=0})
}
async fn list(State(pool): State<SqlitePool>) -> impl IntoResponse {
    match sqlx::query("SELECT id,title,done FROM tasks ORDER BY id")
        .fetch_all(&pool)
        .await
    {
        Ok(rows) => (
            StatusCode::OK,
            Json(Value::Array(rows.iter().map(task).collect())),
        ),
        Err(error) => {
            tracing::error!(operation="list",error=%error);
            (
                StatusCode::SERVICE_UNAVAILABLE,
                Json(json!({"error":"database"})),
            )
        }
    }
}
async fn add(
    State(pool): State<SqlitePool>,
    headers: HeaderMap,
    Json(input): Json<Value>,
) -> impl IntoResponse {
    let title = match input.get("title").and_then(Value::as_str).map(str::trim) {
        Some(title) if !title.is_empty() && title.chars().count() <= 80 => title,
        _ => {
            return (
                StatusCode::BAD_REQUEST,
                Json(json!({"error":"invalid title"})),
            );
        }
    };
    let key = match headers.get("idempotency-key").and_then(|h| h.to_str().ok()) {
        Some(key)
            if !key.is_empty()
                && key.len() <= 64
                && key
                    .bytes()
                    .all(|b| b.is_ascii_alphanumeric() || b == b'-' || b == b'_') =>
        {
            key
        }
        _ => {
            return (
                StatusCode::BAD_REQUEST,
                Json(json!({"error":"idempotency key required"})),
            );
        }
    };
    let request_id = headers
        .get("x-request-id")
        .and_then(|h| h.to_str().ok())
        .filter(|id| {
            !id.is_empty()
                && id.len() <= 64
                && id
                    .bytes()
                    .all(|b| b.is_ascii_alphanumeric() || b == b'-' || b == b'_')
        })
        .unwrap_or("generated-local");
    tracing::info!(operation = "create", request_id, "request accepted");
    let result: Result<(StatusCode, Value), sqlx::Error> = async {
        let mut transaction = pool.begin().await?;
        if let Some(row) = sqlx::query("SELECT id,title,done FROM tasks WHERE request_key=?1")
            .bind(key)
            .fetch_optional(&mut *transaction)
            .await?
        {
            let matches = row.get::<String, _>("title") == title;
            let value = if matches {
                task(&row)
            } else {
                json!({"error":"idempotency conflict"})
            };
            transaction.commit().await?;
            return Ok((
                if matches {
                    StatusCode::OK
                } else {
                    StatusCode::CONFLICT
                },
                value,
            ));
        }
        let row = sqlx::query(
            "INSERT INTO tasks(title,request_key) VALUES(?1,?2) RETURNING id,title,done",
        )
        .bind(title)
        .bind(key)
        .fetch_one(&mut *transaction)
        .await?;
        let value = task(&row);
        transaction.commit().await?;
        Ok((StatusCode::CREATED, value))
    }
    .await;
    match result {
        Ok((status, value)) => (status, Json(value)),
        Err(error) => {
            tracing::error!(operation="create",request_id,error=%error);
            (
                StatusCode::SERVICE_UNAVAILABLE,
                Json(json!({"error":"database"})),
            )
        }
    }
}
async fn ready(State(pool): State<SqlitePool>) -> StatusCode {
    if sqlx::query("SELECT id FROM tasks LIMIT 1")
        .fetch_optional(&pool)
        .await
        .is_ok()
    {
        StatusCode::OK
    } else {
        StatusCode::SERVICE_UNAVAILABLE
    }
}
#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    tracing_subscriber::fmt()
        .with_env_filter(std::env::var("RUST_LOG").unwrap_or_else(|_| "info".into()))
        .init();
    let raw = std::env::var("PORT").unwrap_or_else(|_| "8080".into());
    if raw.is_empty() || !raw.bytes().all(|b| b.is_ascii_digit()) {
        return Err("invalid PORT".into());
    }
    let port = raw.parse::<u16>()?;
    if port < 1024 {
        return Err("PORT must be 1024..=65535".into());
    }
    let url = std::env::var("DATABASE_URL").unwrap_or_else(|_| "sqlite://tasks.db".into());
    let options = SqliteConnectOptions::from_str(&url)?
        .create_if_missing(true)
        .foreign_keys(true)
        .busy_timeout(Duration::from_secs(2));
    // One connection keeps the teaching service's read/insert idempotency transaction
    // serialized. Scaling the pool requires a separate contention/retry exercise.
    let pool = SqlitePoolOptions::new()
        .max_connections(1)
        .connect_with(options)
        .await?;
    sqlx::raw_sql(include_str!("../migrations/001.sql"))
        .execute(&pool)
        .await?;
    sqlx::query("SELECT id,title,done,request_key FROM tasks LIMIT 0")
        .execute(&pool)
        .await?;
    let app = Router::new()
        .route("/health", get(|| async { Json(json!({"ok":true})) }))
        .route("/ready", get(ready))
        .route("/tasks", get(list).post(add))
        .layer(DefaultBodyLimit::max(65536))
        .with_state(pool);
    let listener = tokio::net::TcpListener::bind(("0.0.0.0", port)).await?;
    tracing::info!(port, "listening");
    axum::serve(listener, app)
        .with_graceful_shutdown(async {
            let _ = tokio::signal::ctrl_c().await;
        })
        .await?;
    Ok(())
}
#[cfg(test)]
mod tests {
    #[tokio::test]
    async fn schema_rejects_invalid_writes_and_preserves_rows() {
        let pool = sqlx::sqlite::SqlitePoolOptions::new()
            .max_connections(1)
            .connect("sqlite::memory:")
            .await
            .unwrap();
        sqlx::raw_sql(include_str!("../migrations/001.sql"))
            .execute(&pool)
            .await
            .unwrap();
        sqlx::query("INSERT INTO tasks(title,request_key) VALUES('learn','key')")
            .execute(&pool)
            .await
            .unwrap();
        assert!(
            sqlx::query("INSERT INTO tasks(title,request_key) VALUES('','other')")
                .execute(&pool)
                .await
                .is_err()
        );
        assert!(
            sqlx::query("INSERT INTO tasks(title,request_key) VALUES('other','key')")
                .execute(&pool)
                .await
                .is_err()
        );
        let count: i64 = sqlx::query_scalar("SELECT count(*) FROM tasks")
            .fetch_one(&pool)
            .await
            .unwrap();
        assert_eq!(count, 1);
    }
}
