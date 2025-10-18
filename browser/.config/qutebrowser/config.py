# pylint: disable=C0111
c = c  # noqa: F821 pylint: disable=E0602,C0103
config = config  # noqa: F821 pylint: disable=E0602,C0103

config.load_autoconfig()

# General settings
c.url.start_pages = ["https://start.duckduckgo.com"]
c.url.default_page = "https://start.duckduckgo.com"
c.auto_save.session = True
c.confirm_quit = ["multiple-tabs"]

# Downloads
c.downloads.location.directory = "~/Downloads"
c.downloads.location.prompt = False
c.downloads.location.remember = True
c.downloads.remove_finished = 3000

# Appearance
c.colors.webpage.darkmode.enabled = True
c.colors.webpage.darkmode.policy.images = "smart"
c.statusbar.show = "in-mode"
c.tabs.show = "multiple"
c.tabs.position = "top"
c.tabs.padding = {"top": 5, "bottom": 5, "left": 5, "right": 5}
c.scrolling.smooth = True

# Fonts
c.fonts.default_family = "JetBrains Mono Nerd Font"
c.fonts.default_size = "12pt"

# Privacy & Security
c.content.cookies.accept = "no-3rdparty"
c.content.javascript.enabled = True  # Enable only if necessary
c.content.autoplay = False

# Enhanced security without breaking compatibility
c.content.blocking.method = "both"
c.content.blocking.adblock.lists = [
    "https://easylist.to/easylist/easylist.txt",
    "https://easylist.to/easylist/easyprivacy.txt",
    "https://raw.githubusercontent.com/uBlockOrigin/uAssets/master/filters/filters.txt",
]
c.content.headers.do_not_track = True
c.content.media.audio_capture = False
c.content.media.video_capture = False
c.content.notifications.enabled = False
c.content.webrtc_ip_handling_policy = "default-public-interface-only"
c.content.webgl = False
c.content.canvas_reading = False
c.content.geolocation = False
c.content.mouse_lock = False
c.content.desktop_capture = False
c.content.xss_auditing = True  # Provides basic XSS detection

# Search engines
c.url.searchengines = {
    "DEFAULT": "https://duckduckgo.com/?q={}",
    "w": "https://en.wikipedia.org/wiki/{}",
    "yt": "https://www.youtube.com/results?search_query={}",
    "gh": "https://github.com/search?q={}",
    "r": "https://www.reddit.com/search/?q={}",
}

# Key bindings
config.bind("J", "tab-prev")
config.bind("K", "tab-next")
config.bind("<Ctrl-d>", "scroll-page 0 0.5")
config.bind("<Ctrl-u>", "scroll-page 0 -0.5")
config.bind(",m", "spawn mpv {url}")
config.bind(",yt", "hint links spawn mpv {hint-url}")
config.bind(",p", "open -p")  # open in private window

# Editor integration
c.editor.command = ["kitty", "-e", "nvim", "{}"]
