// ─── Zen Appearance and Theme ───
user_pref("zen.theme.border-radius", 0);
user_pref("zen.theme.content-element-separation", 0);
user_pref("zen.theme.accent-color", "#000000");
user_pref("zen.theme.auto-dark-mode", true);
user_pref("zen.theme.dark-mode", true);

// Use system GTK theme integration (Linux)
user_pref("widget.content.allow-gtk-dark-theme", true);
user_pref("widget.chrome.allow-gtk-dark-theme", true);
user_pref("widget.gtk.rounded-bottom-corners.enabled", false);

// ─── Titlebar and Window Controls ───
user_pref("browser.tabs.inTitlebar", 0);
user_pref("zen.view.experimental-no-window-controls", true);

// ─── Compact Layout & UI Behavior ───
user_pref("browser.compactmode.show", true);
user_pref("zen.view.compact.animate-sidebar", false);
user_pref("sidebar.animation.enabled", false);
user_pref("layout.css.prefers-reduced-motion.enabled", true);
user_pref("layout.css.prefers-reduced-transparency.enabled", true);

// ─── Performance & Rendering ───
user_pref("gfx.webrender.all", true);
user_pref("gfx.webrender.compositor", true);
user_pref("gfx.webrender.software", false);
user_pref("gfx.webrender.precache-shaders", true);
user_pref("dom.webgpu.enabled", true);
user_pref("dom.webgpu.wgpu-backend", "vulkan");
user_pref("gfx.webrender.debug.profiler", false); // ensure stable performance

// ─── Memory & Session Management ───
user_pref("browser.sessionstore.max_tabs_undo", 5);
user_pref("browser.sessionstore.interval", 30000);

// ─── Privacy and Network ───
user_pref("network.prefetch-next", false);
user_pref("network.dns.disablePrefetch", true);
user_pref("network.dns.disablePrefetchFromHTTPS", true);
user_pref("network.http.speculative-parallel-limit", 0);
user_pref("browser.urlbar.speculativeConnect.enabled", false);
user_pref("browser.newtabpage.activity-stream.feeds.telemetry", false);
user_pref("browser.newtabpage.activity-stream.telemetry", false);
user_pref("datareporting.healthreport.service.enabled", false);
user_pref("datareporting.policy.dataSubmissionEnabled", false);
user_pref("toolkit.telemetry.unified", false);
user_pref("toolkit.telemetry.enabled", false);

// ─── Standards & Rendering ───
user_pref("svg.context-properties.content.enabled", true);
user_pref("layout.css.color-mix.enabled", true);

// ─── Dark Mode and System Integration ───
user_pref("layout.css.prefers-color-scheme.content-override", 2);
user_pref("ui.systemUsesDarkTheme", 1);
user_pref("browser.theme.toolbar-theme", 0);
user_pref("browser.theme.content-theme", 0);

// ─── Misc Zen-Specific UX ───
user_pref("zen.sidebar.experimental.float", false);
user_pref("zen.sidebar.experimental.auto-hide", false);
user_pref("zen.experimental.workspaces.enabled", true);
user_pref("zen.view.show-clear-tabs-button", false);
