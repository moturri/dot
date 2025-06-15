# Load existing autoconfig.yaml if present
config.load_autoconfig()

# General settings
c.url.start_pages = ["https://start.duckduckgo.com"]
c.url.default_page = "https://start.duckduckgo.com"
c.downloads.location.directory = "~/Downloads"
c.auto_save.session = True

# Appearance
c.colors.webpage.darkmode.enabled = True
c.colors.webpage.darkmode.policy.images = "smart"
c.statusbar.show = "in-mode"
c.tabs.show = "multiple"
c.tabs.position = "top"
c.tabs.padding = {"top": 5, "bottom": 5, "left": 5, "right": 5}

# Fonts
c.fonts.default_family = "JetBrains Mono Nerd Font"
c.fonts.default_size = "12pt"

# Privacy & Security
c.content.cookies.accept = "no-3rdparty"
c.content.javascript.enabled = True  # Some sites need this, disable if you want max security
c.content.autoplay = False
c.content.blocking.method = "both"
c.content.blocking.adblock.lists = [
    "https://easylist.to/easylist/easylist.txt",
    "https://easylist.to/easylist/easyprivacy.txt",
    "https://raw.githubusercontent.com/uBlockOrigin/uAssets/master/filters/filters.txt"
]

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

# Downloads
c.downloads.remove_finished = 3000

# Misc UX
c.scrolling.smooth = True
c.confirm_quit = ["multiple-tabs"]
c.editor.command = ["kitty", "-e", "nvim", "{}"]

# Disable notifications (can be noisy)
c.content.notifications.enabled = False

