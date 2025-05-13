return {
  {
    "tpope/vim-fugitive",
    version = "*",
  },
  {
    "lewis6991/gitsigns.nvim",
    version = "*",
    config = function()
      local gitsigns = require("gitsigns")

      -- Default configuration for GitSigns
      gitsigns.setup({
        signs = {
          add = { text = " " },
          change = { text = " " },
          delete = { text = " " },
          topdelete = { text = " " },
          changedelete = { text = "󰐕 " },
          untracked = { text = " " },
          renamed = { text = "󰁕 " },
          ignored = { text = " " },
          unstaged = { text = "󰄱 " },
          staged = { text = " " },
          conflict = { text = " " },
        },
        preview_config = {
          border = "rounded", -- Preview border style
        },
        current_line_blame = false,
        current_line_blame_opts = {
          virt_text = true,
          virt_text_pos = "eol",
          delay = 500,
        },
        on_attach = function(bufnr)
          -- Local alias to `gitsigns`
          local gs = package.loaded.gitsigns

          -- Helper function to map keys with buffer-specific options
          local function map(mode, lhs, rhs, opts)
            opts = opts or {}
            opts.buffer = bufnr
            vim.keymap.set(mode, lhs, rhs, opts)
          end

          -- Key mappings for navigation and actions
          map("n", "]c", function()
            if vim.wo.diff then
              return "]c"
            end
            vim.schedule(function()
              gs.next_hunk()
            end)
            return "<Ignore>"
          end, { expr = true })

          map("n", "[c", function()
            if vim.wo.diff then
              return "[c"
            end
            vim.schedule(function()
              gs.prev_hunk()
            end)
            return "<Ignore>"
          end, { expr = true })

          -- Git action mappings
          map("n", "<leader>gp", gs.preview_hunk)
          map("n", "<leader>gt", gs.toggle_current_line_blame)
          map("n", "<leader>ga", gs.stage_hunk)
          map("n", "<leader>gs", gs.undo_stage_hunk)
          map("n", "<leader>gq", gs.diffthis)
          map("n", "<leader>gR", gs.reset_hunk)
          map("n", "<leader>gl", ":Git log<CR>")
        end,
      })
    end,
  },
}
