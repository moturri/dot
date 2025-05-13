return {
  "nvim-neo-tree/neo-tree.nvim",
  version = "*",
  dependencies = {
    "nvim-lua/plenary.nvim",
    "nvim-tree/nvim-web-devicons",
    "MunifTanjim/nui.nvim",
  },
  config = function()
    require("neo-tree").setup({
      close_if_last_window = true,
      enable_diagnostics = true,

      -- Neo-tree window configuration
      window = {
        position = "left", -- Placing Neo-tree to the left of the window
        width = 35,        -- Set the width to 35 for a more compact file explorer
      },

      -- Filesystem config
      filesystem = {
        filtered_items = {
          visible = true,
          hide_dotfiles = false,  -- Change this based on your preference
          hide_gitignored = true, -- Hide git-ignored files for clarity
        },
        follow_current_file = {
          enabled = true,                       -- Follow the current file being edited in Neo-tree
        },
        hijack_netrw_behavior = "open_default", -- Prevent netrw from interfering with Neo-tree
      },

      -- Default component configs (Git status, etc.)
      default_component_configs = {
        name = {
          trailing_slash = true,        -- Display trailing slashes to distinguish directories
          use_git_status_colors = true, -- Enable git status coloring
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

      -- Neo-tree render configuration
      render = {
        highlight_opened_files = "all", -- Highlight files that are open
        add_trailing = true,            -- Add trailing slashes to directories
      },

      -- Auto-refresh tree
      auto_refresh = true,

      -- Buffers section
      buffers = {
        use_git_status_colors = true, -- Use git status colors in the buffers view
        show_unloaded = true,         -- Show unloaded buffers as well
        show_only_in_buffers = true,  -- Show only open buffers in the Neo-tree
      },

      -- Float window configuration
      float = {
        enable = true,         -- Enable floating window
        quit_on_escape = true, -- Allow closing with ESC key
        size = {
          width = 0.8,         -- Set the width of the floating window as a percentage of the screen
          height = 0.8,        -- Set the height of the floating window as a percentage of the screen
        },
        position = "center",   -- Position the floating window in the center
      },
    })

    -- Keymap for toggling Neo-tree
    vim.keymap.set("n", "<C-n>", "<cmd>Neotree toggle<CR>", { noremap = true, silent = true })

    -- Keymap to open Neo-tree in a floating window
    vim.keymap.set("n", "<leader>fs", "<cmd>Neotree float<CR>", { noremap = true, silent = true })

    -- Keymap for opening Neo-tree buffers
    vim.keymap.set("n", "<leader>bf", "<cmd>Neotree buffers reveal float<CR>", { noremap = true, silent = true })
  end,
}
