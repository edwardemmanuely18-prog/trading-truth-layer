#![cfg_attr(mobile, tauri::mobile_entry_point)]

use tauri_plugin_store::Builder as StoreBuilder;
use tauri_plugin_window_state::Builder as WindowStateBuilder;

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()

        // WINDOW STATE PERSISTENCE
        .plugin(WindowStateBuilder::default().build())

        // LOCAL DESKTOP STORAGE
        .plugin(StoreBuilder::default().build())

        // DEVELOPMENT LOGGING
        .setup(|app| {
            if cfg!(debug_assertions) {
                app.handle().plugin(
                    tauri_plugin_log::Builder::default()
                        .level(log::LevelFilter::Info)
                        .build(),
                )?;
            }

            println!("Trading Truth Layer Desktop Runtime Initialized");

            Ok(())
        })

        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}