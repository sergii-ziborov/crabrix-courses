FROM rust:1.99-bookworm AS build
WORKDIR /src
COPY Cargo.toml Cargo.lock ./
COPY src ./src
COPY migrations ./migrations
RUN cargo build --locked --release
FROM debian:bookworm-slim
RUN useradd --create-home --uid 10001 app && mkdir /data && chown app /data
COPY --from=build /src/target/release/task-ledger-server /usr/local/bin/task-ledger-server
USER app
WORKDIR /data
ENV PORT=8080 DATABASE_URL=sqlite:///data/tasks.db
EXPOSE 8080
ENTRYPOINT ["task-ledger-server"]
