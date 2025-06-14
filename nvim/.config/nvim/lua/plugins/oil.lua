return {
  {
    "stevearc/oil.nvim",
    cmd = { "Oil" }, -- Lazy load on Oil command
    keys = {
      { "-",         function() require("oil").toggle_float() end, desc = "Toggle Oil Floating Explorer" },
      { "<leader>e", function() require("oil").toggle_float() end, desc = "Toggle Oil Floating Explorer" },
    },
    config = function()
      local ok, oil = pcall(require, "oil")
      if not ok then
        vim.notify("Oil.nvim not found!", vim.log.levels.ERROR)
        return
      end

      oil.setup({
        default_file_explorer = true,
        columns = { "icon", "permissions", "size", "mtime" },
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

      -- Disable line numbers in Oil buffers
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
