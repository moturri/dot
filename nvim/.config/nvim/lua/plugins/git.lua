return {
  {
    "tpope/vim-fugitive",
    version = "*",
  },
  {
    "lewis6991/gitsigns.nvim",
    version = "*",
    opts = {
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
        border = "rounded",
      },
      current_line_blame = false,
      current_line_blame_opts = {
        virt_text = true,
        virt_text_pos = "eol",
        delay = 500,
      },
    },
    config = function(_, opts)
      local gitsigns = require("gitsigns")
      gitsigns.setup(opts)

      -- on_attach keybindings
      gitsigns.attach = function(bufnr)
        local gs = package.loaded.gitsigns
        local map = function(mode, lhs, rhs, map_opts)
          map_opts = vim.tbl_extend("force", { buffer = bufnr }, map_opts or {})
          vim.keymap.set(mode, lhs, rhs, map_opts)
        end

        -- Navigation
        map("n", "]c", function()
          if vim.wo.diff then
            return "]c"
          end
          vim.schedule(gs.next_hunk)
          return "<Ignore>"
        end, { expr = true })

        map("n", "[c", function()
          if vim.wo.diff then
            return "[c"
          end
          vim.schedule(gs.prev_hunk)
          return "<Ignore>"
        end, { expr = true })

        -- Actions
        map("n", "<leader>gp", gs.preview_hunk)
        map("n", "<leader>gt", gs.toggle_current_line_blame)
        map("n", "<leader>ga", gs.stage_hunk)
        map("n", "<leader>gs", gs.undo_stage_hunk)
        map("n", "<leader>gq", gs.diffthis)
        map("n", "<leader>gR", gs.reset_hunk)

        -- Fugitive shortcut
        map("n", "<leader>gl", "<cmd>Git log<CR>")
      end
    end,
  },
}
