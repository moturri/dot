// user.js configuration file

// Appearance and Theme Tweaks
user_pref("zen.theme.border-radius", 0);
user_pref("zen.theme.content-element-separation", 0);
user_pref("zen.theme.accent-color", "#6f67e0");
user_pref("widget.gtk.rounded-bottom-corners.enabled", false);
user_pref("browser.tabs.inTitlebar", 0);

// UI/UX Behavior & Compact Layout
user_pref("browser.compactmode.show", true);
user_pref("zen.view.compact.animate-sidebar", false);
user_pref("sidebar.animation.enabled", false);
user_pref("layout.css.prefers-reduced-motion.enabled", true);
user_pref("layout.css.prefers-reduced-transparency.enabled", true);

// Window and Experimental UI Features
user_pref("zen.view.experimental-no-window-controls", true);

// Performance & Hardware Acceleration
user_pref("gfx.webrender.all", true);
user_pref("gfx.webrender.compositor", true);
user_pref("dom.webgpu.enabled", true);
user_pref("dom.webgpu.wgpu-backend", "vulkan");

// SVG and Web Standards
user_pref("svg.context-properties.content.enabled", true);

// Telemetry
user_pref("datareporting.healthreport.service.enabled", false);
