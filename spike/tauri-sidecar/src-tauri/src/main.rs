// PROTOTYPE: spawn the frozen sidecar, capture its port, expose port+token to the UI.
use std::sync::Mutex;
use tauri::{Manager, State};
use tauri_plugin_shell::{process::CommandEvent, ShellExt};

struct Keep(Mutex<Option<tauri_plugin_shell::process::CommandChild>>);

#[derive(Default)]
struct Info(Mutex<Option<(u16, String)>>);

#[tauri::command]
async fn sidecar_info(state: State<'_, Info>) -> Result<serde_json::Value, String> {
    for _ in 0..600 {
        if let Some((p, t)) = state.0.lock().unwrap().clone() {
            return Ok(serde_json::json!({ "port": p, "token": t }));
        }
        tokio_sleep().await;
    }
    Err("sidecar did not report a port in 60s".into())
}

#[tauri::command]
fn ui_report(msg: String) {
    if let Ok(p) = std::env::var("SPIKE_REPORT") {
        use std::io::Write;
        if let Ok(mut f) = std::fs::OpenOptions::new().create(true).append(true).open(p) {
            let _ = writeln!(f, "ui: {msg}");
        }
    }
}

async fn tokio_sleep() {
    tauri::async_runtime::spawn_blocking(|| std::thread::sleep(std::time::Duration::from_millis(100)))
        .await
        .ok();
}

fn main() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .manage(Info::default())
        .invoke_handler(tauri::generate_handler![sidecar_info, ui_report])
        .setup(|app| {
            let token = format!("{:x}{:x}", std::process::id(), std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH).unwrap().as_nanos());
            let (mut rx, child) = app.shell().sidecar("ddoloot-sidecar")?
                .env("DDOLOOT_TOKEN", token.clone()).spawn()?;
            app.manage(Keep(Mutex::new(Some(child)))); // keep stdin pipe open: dropping it = EOF = sidecar exits
            let handle = app.handle().clone();
            tauri::async_runtime::spawn(async move {
                while let Some(ev) = rx.recv().await {
                    if let CommandEvent::Stdout(line) = ev {
                        let s = String::from_utf8_lossy(&line);
                        if let Some(p) = s.trim().strip_prefix("PORT=") {
                            if let Ok(p) = p.parse::<u16>() {
                                *handle.state::<Info>().0.lock().unwrap() = Some((p, token.clone()));
                            }
                        }
                    }
                }
            });
            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error running app");
}
