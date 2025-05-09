return {
  {
    "stevearc/oil.nvim",
    version = "*",
    config = function()
      local oil = require("oil")

      oil.setup({
        default_file_explorer = true,
        columns = {
          "icon",
          "permissions",
          "size",
          "mtime",
        },
        view_options = {
          show_hidden = true,
        },
        float = {
          border = "rounded",
          max_width = 0.8,
          max_height = 0.8,
        },
        keymaps = {
          ["<C-v>"] = "actions.select_vsplit",
          ["<C-s>"] = "actions.select_split",
          ["<C-t>"] = "actions.select_tab",
        },
      })

      -- Keymaps
      vim.keymap.set("n", "-", oil.toggle_float, { desc = "Toggle Oil (Float)" })
      vim.keymap.set("n", "<leader>e", oil.toggle_float, { desc = "Toggle Oil (Float)" })

      -- Optional: Disable line numbers in Oil buffers
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
