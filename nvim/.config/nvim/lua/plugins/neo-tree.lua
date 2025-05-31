return {
  "nvim-neo-tree/neo-tree.nvim",
  version = "*",
  dependencies = {
    "nvim-lua/plenary.nvim",
    "nvim-tree/nvim-web-devicons",
    {
      "MunifTanjim/nui.nvim",
      version = "*",
    },
  },
  opts = {
    close_if_last_window = true,
    enable_diagnostics = true,
    window = {
      position = "left",
      width = 40,
    },
    filesystem = {
      filtered_items = {
        visible = true,
        hide_dotfiles = false,
        -- hide_gitignored = false,
      },
      follow_current_file = {
        enabled = true,
      },
      hijack_netrw_behavior = "open_default",
    },
    default_component_configs = {
      name = {
        trailing_slash = true,
        use_git_status_colors = true,
      },
      git_status = {
        symbols = {
          added = " ",
          modified = " ",
          deleted = " ",
          renamed = "󰁕 ",
          untracked = " ",
          ignored = " ",
          unstaged = "󰄱 ",
          staged = " ",
          conflict = " ",
        },
      },
    },
  },
  config = function(_, opts)
    require("neo-tree").setup(opts)

    -- Keybindings
    local keymap = vim.keymap.set
    local opts_map = { noremap = true, silent = true }

    keymap("n", "<C-n>", "<cmd>Neotree reveal toggle<CR>", opts_map)
    keymap("n", "<leader>bf", "<cmd>Neotree buffers reveal float<CR>", opts_map)
    keymap("n", "<leader>fs", "<cmd>Neotree float<CR>", opts_map)
  end,
}
