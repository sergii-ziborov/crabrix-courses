"""Executable counterexamples for the corrected contracts, not prose snapshots."""
import json
import subprocess
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main():
    results = []
    cases = {
        "drop-locals-and-fields": ('''struct D(&'static str);
impl Drop for D { fn drop(&mut self) { println!("{}", self.0); } }
struct Pair { _first: D, _second: D }
fn main() { let _a = D("local-first"); let _b = D("local-second");
let _pair = Pair { _first: D("field-first"), _second: D("field-second") }; }
''', "field-first\nfield-second\nlocal-second\nlocal-first\n"),
        "associated-type-per-instantiation": ('''trait Convert<T> { type Output; fn convert(self) -> Self::Output; }
struct Unit;
impl Convert<u8> for Unit { type Output = u8; fn convert(self) -> u8 { 8 } }
impl Convert<u16> for Unit { type Output = u16; fn convert(self) -> u16 { 16 } }
fn main() { assert_eq!(<Unit as Convert<u8>>::convert(Unit), 8);
assert_eq!(<Unit as Convert<u16>>::convert(Unit), 16); }
''', ""),
        "move-can-be-fn-and-spawn-can-borrow-static": ('''static MESSAGE: &str = "static";
fn twice<F: Fn() -> usize>(f: F) { assert_eq!(f(), 3); assert_eq!(f(), 3); }
fn main() { let name = String::from("ada"); twice(move || name.len());
assert_eq!(std::thread::spawn(|| MESSAGE).join().unwrap(), "static");
let large = [0_u8; 65536]; let copied = large; assert_eq!(large, copied); }
''', ""),
        "channel-drains-after-disconnect": ('''fn main() { let (tx, rx) = std::sync::mpsc::channel();
tx.send(1).unwrap(); tx.send(2).unwrap(); drop(tx);
assert_eq!(rx.into_iter().collect::<Vec<_>>(), vec![1, 2]); }
''', ""),
    }
    with tempfile.TemporaryDirectory(prefix="crabrix-senior-") as tmp:
        root = Path(tmp)
        for name, (source, expected) in cases.items():
            src = root / (name + ".rs"); src.write_text(source)
            binary = root / name
            subprocess.run(["rustc", "--edition=2024", str(src), "-o", str(binary)], check=True, capture_output=True)
            run = subprocess.run([str(binary)], check=True, capture_output=True, text=True, timeout=10)
            assert run.stdout == expected, (name, run.stdout)
            results.append({"case": name, "passed": True})
        src = root / "not-send.rs"
        src.write_text('fn main() { let value = std::rc::Rc::new(1); std::thread::spawn(move || drop(value)); }')
        run = subprocess.run(["rustc", "--edition=2024", str(src)], cwd=root, capture_output=True, text=True)
        assert run.returncode != 0 and "E0277" in run.stderr
        results.append({"case": "move-does-not-make-rc-send", "passed": True})
        src = root / "cfg.rs"
        src.write_text('#[cfg(test)] #[test] fn test_even_with_optimization() { assert!(cfg!(test)); }\n#[cfg(not(test))] fn main() {}')
        binary = root / "optimized-tests"
        subprocess.run(["rustc", "--edition=2024", "--test", "-O", str(src), "-o", str(binary)], check=True, capture_output=True)
        run = subprocess.run([str(binary)], check=True, capture_output=True, text=True)
        assert "1 passed" in run.stdout
        results.append({"case": "optimized-test-build-retains-cfg-test", "passed": True})
        (root / "Cargo.toml").write_text('[package]\nname="senior-semantics"\nversion="0.1.0"\nedition="2024"\n[dependencies]\ntokio={version="=1.54.1",default-features=false,features=["rt","sync"]}\n')
        (root / "src").mkdir()
        (root / "src/main.rs").write_text('''fn main() {
let rt = tokio::runtime::Builder::new_current_thread().build().unwrap();
rt.block_on(async {
    let (tx, rx) = tokio::sync::oneshot::channel();
    let handle = tokio::spawn(async move { tx.send(7).unwrap(); });
    drop(handle);
    assert_eq!(rx.await.unwrap(), 7); // task survives its handle
    let handle = tokio::spawn(std::future::pending::<()>());
    handle.abort();
    assert!(handle.await.unwrap_err().is_cancelled());
}); }
''')
        subprocess.run(["cargo", "generate-lockfile", "--offline"], cwd=root, check=True, capture_output=True)
        subprocess.run(["cargo", "run", "--quiet", "--offline", "--locked"], cwd=root, check=True, capture_output=True, timeout=120)
        results.append({"case": "tokio-handle-drop-detaches-abort-observes-cancellation", "passed": True})
    receipt = {"scope": "Desktop compiler semantic examples; not native/browser runtime qualification", "checks": results}
    (HERE / "verification.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
