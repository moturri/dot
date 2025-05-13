return {
  {
    "stevearc/oil.nvim",
    version = "*",
    config = function()
      local oil = require("oil")

      -- Setup oil.nvim with customized options
      oil.setup({
        -- Default file explorer behavior
        default_file_explorer = true,

        -- Columns to display in file explorer
        columns = {
          "icon",        -- Show icon
          "permissions", -- Show file permissions
          "size",        -- Show file size
          "mtime",       -- Show last modified time
        },

        -- Options to show hidden files
        view_options = {
          show_hidden = true, -- Show hidden files
        },

        -- Floating window options
        float = {
          border = "rounded", -- Rounded borders for the floating window
          max_width = 0.8,    -- Max width of the float (80% of screen width)
          max_height = 0.8,   -- Max height of the float (80% of screen height)
        },

        -- Keymaps for opening files
        keymaps = {
          ["<C-v>"] = "actions.select_vsplit", -- Open file in vertical split
          ["<C-s>"] = "actions.select_split",  -- Open file in horizontal split
          ["<C-t>"] = "actions.select_tab",    -- Open file in new tab
        },
      })

      -- Toggle oil file explorer with specific keymaps
      vim.keymap.set("n", "-", oil.toggle_float, { desc = "Toggle Oil (Float)" })
      vim.keymap.set("n", "<leader>e", oil.toggle_float, { desc = "Toggle Oil (Float)" })

      -- Optional: Disable line numbers in oil buffers for a cleaner view
      vim.api.nvim_create_autocmd("FileType", {
        pattern = "oil",
        callback = function()
          vim.wo.number = false
          vim.wo.relativenumber = false
        end,
      })
    end,
  },
}
