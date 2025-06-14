return {
  "goolord/alpha-nvim",
  dependencies = {
    "nvim-tree/nvim-web-devicons",
  },
  config = function()
    local ok, alpha = pcall(require, "alpha")
    if not ok then
      vim.notify("Alpha-nvim failed to load", vim.log.levels.ERROR)
      return
    end

    local dashboard = require("alpha.themes.startify")

    dashboard.section.header.val = {
      [[                                                                    ]],
      [[       ████ ██████           █████      ██                   ]],
      [[      ███████████             █████                         ]],
      [[      █████████ ███████████████████ ███   ███████████  ]],
      [[     █████████  ███    █████████████ █████ ██████████████   ]],
      [[    █████████ ██████████ █████████ █████ █████ ████ █████   ]],
      [[  ███████████ ███    ███ █████████ █████ █████ ████ █████  ]],
      [[ ██████  █████████████████████ ████ █████ █████ ████ ██████ ]],
    }

    -- dashboard.section.footer.val = {
    --   dashboard.button("f", "󰈞  Find File", ":Telescope find_files<CR>"),
    --   dashboard.button("r", "  Recent", ":Telescope oldfiles<CR>"),
    -- }

    alpha.setup(dashboard.opts)
  end,
}
