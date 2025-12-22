// ZEN BROWSER – MINIMAL / DARK / PRIVATE / PERFORMANCE (ARCH LINUX)

// ZEN THEME & APPEARANCE
user_pref("zen.theme.border-radius", 0);
user_pref("zen.theme.content-element-separation", 0);
user_pref("zen.theme.accent-color", "#000000");
user_pref("zen.theme.auto-dark-mode", true);
user_pref("zen.theme.dark-mode", true);

// GTK integration (Linux)
user_pref("widget.content.allow-gtk-dark-theme", true);
user_pref("widget.chrome.allow-gtk-dark-theme", true);
user_pref("widget.gtk.rounded-bottom-corners.enabled", false);

// WINDOW / TITLEBAR
user_pref("browser.tabs.inTitlebar", 0);
user_pref("zen.view.experimental-no-window-controls", true);

// UI DENSITY & MOTION
user_pref("browser.compactmode.show", true);

user_pref("zen.view.compact.animate-sidebar", false);
user_pref("sidebar.animation.enabled", false);

user_pref("layout.css.prefers-reduced-motion.enabled", true);
user_pref("layout.css.prefers-reduced-transparency.enabled", true);

// DARK MODE / COLOR SCHEME
user_pref("ui.systemUsesDarkTheme", 1);
user_pref("layout.css.prefers-color-scheme.content-override", 2);

user_pref("browser.theme.toolbar-theme", 0);
user_pref("browser.theme.content-theme", 0);

// PERFORMANCE & RENDERING
user_pref("gfx.webrender.all", true);
user_pref("gfx.webrender.compositor", true);
user_pref("gfx.webrender.software", false);
user_pref("gfx.webrender.precache-shaders", true);

user_pref("dom.webgpu.enabled", true);
user_pref("dom.webgpu.wgpu-backend", "vulkan");

// STANDARDS / MODERN CSS
user_pref("svg.context-properties.content.enabled", true);
user_pref("layout.css.color-mix.enabled", true);

// SESSION & MEMORY
user_pref("browser.sessionstore.max_tabs_undo", 5);
user_pref("browser.sessionstore.interval", 30000);

// ZEN UX FEATURES
user_pref("zen.experimental.workspaces.enabled", true);

user_pref("zen.sidebar.experimental.float", false);
user_pref("zen.sidebar.experimental.auto-hide", false);

user_pref("zen.view.show-clear-tabs-button", false);

// PRIVACY HARDENING (ARKENFOX-STYLE, CURATED)

// QUIETER FIREFOX
user_pref("browser.aboutConfig.showWarning", false);
user_pref("browser.discovery.enabled", false);
user_pref("extensions.getAddons.showPane", false);
user_pref("extensions.htmlaboutaddons.recommendations.enabled", false);

// TELEMETRY / STUDIES
user_pref("toolkit.telemetry.enabled", false);
user_pref("toolkit.telemetry.unified", false);
user_pref("toolkit.telemetry.archive.enabled", false);
user_pref("toolkit.telemetry.shutdownPingSender.enabled", false);
user_pref("toolkit.telemetry.updatePing.enabled", false);
user_pref("toolkit.telemetry.newProfilePing.enabled", false);
user_pref("toolkit.telemetry.firstShutdownPing.enabled", false);

user_pref("datareporting.healthreport.service.enabled", false);
user_pref("datareporting.policy.dataSubmissionEnabled", false);

user_pref("app.shield.optoutstudies.enabled", false);
user_pref("normandy.enabled", false);
user_pref("normandy.app_update_url", "");

// NETWORK & PREFETCHING
user_pref("network.prefetch-next", false);
user_pref("network.dns.disablePrefetch", true);
user_pref("network.dns.disablePrefetchFromHTTPS", true);
user_pref("network.predictor.enabled", false);
user_pref("network.predictor.enable-prefetch", false);
user_pref("network.http.speculative-parallel-limit", 0);
user_pref("browser.urlbar.speculativeConnect.enabled", false);
user_pref("link.prefetching.enabled", false);
user_pref("network.preload", false);

// SEARCH / URL BAR
user_pref("browser.search.suggest.enabled", false);
user_pref("browser.urlbar.suggest.searches", false);
user_pref("browser.urlbar.suggest.history", false);
user_pref("browser.urlbar.suggest.openpage", false);
user_pref("browser.urlbar.suggest.remotetab", false);
user_pref("browser.urlbar.suggest.topsites", false);
user_pref("browser.formfill.enable", false);

// PASSWORDS
user_pref("signon.rememberSignons", false);
user_pref("signon.autofillForms", false);
user_pref("signon.formlessCapture.enabled", false);

// CACHE / STORAGE
user_pref("browser.cache.disk.enable", false);
user_pref("browser.cache.memory.enable", true);

// HTTPS / CONTENT SECURITY
user_pref("dom.security.https_only_mode", true);
user_pref("security.mixed_content.block_active_content", true);
user_pref("security.mixed_content.block_display_content", true);

// REFERERS
user_pref("network.http.referer.XOriginPolicy", 2);
user_pref("network.http.referer.XOriginTrimmingPolicy", 2);

// TRACKING PROTECTION
user_pref("browser.contentblocking.category", "strict");
user_pref("privacy.trackingprotection.enabled", true);
user_pref("privacy.trackingprotection.socialtracking.enabled", true);

// SHUTDOWN SANITIZATION
user_pref("privacy.sanitize.sanitizeOnShutdown", true);
user_pref("privacy.clearOnShutdown.cache", true);
user_pref("privacy.clearOnShutdown.cookies", true);
user_pref("privacy.clearOnShutdown.history", true);
user_pref("privacy.clearOnShutdown.sessions", true);
user_pref("privacy.clearOnShutdown.formdata", true);
user_pref("privacy.clearOnShutdown.sites", true);

// HARD PRIVACY CUTS
user_pref("webgl.disabled", true);
user_pref("media.peerconnection.enabled", false);
