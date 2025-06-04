return {
  {
    "tpope/vim-fugitive",
    version = "*",
    cmd = { "Git", "G" }, -- Lazy load on Git commands
  },
  {
    "lewis6991/gitsigns.nvim",
    version = "*",
    event = { "BufReadPre", "BufNewFile" }, -- Lazy load on buffer read
    opts = {
      signs = {
        add          = { text = " " },
        change       = { text = " " },
        delete       = { text = " " },
        topdelete    = { text = " " },
        changedelete = { text = "󰐕 " },
        untracked    = { text = " " },
        renamed      = { text = "󰁕 " },
        ignored      = { text = " " },
        unstaged     = { text = "󰄱 " },
        staged       = { text = " " },
        conflict     = { text = " " },
      },
      preview_config = {
        border = "rounded",
      },
      current_line_blame = false, -- Disable by default, toggle with <leader>gt
      current_line_blame_opts = {
        virt_text = true,
        virt_text_pos = "eol",
        delay = 500,
      },
      on_attach = function(bufnr)
        local gs = package.loaded.gitsigns
        local map = function(mode, lhs, rhs, opts)
          opts = vim.tbl_extend("force", { buffer = bufnr }, opts or {})
          vim.keymap.set(mode, lhs, rhs, opts)
        end

        -- Navigation between hunks
        map("n", "]c", function()
          if vim.wo.diff then return "]c" end
          vim.schedule(gs.next_hunk)
          return "<Ignore>"
        end, { expr = true })

        map("n", "[c", function()
          if vim.wo.diff then return "[c" end
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
        map("n", "<leader>gB", gs.toggle_deleted) -- Toggle showing deleted lines

        -- Visual mode mappings for staging/resetting selected hunks
        map("v", "<leader>ga", function()
          gs.stage_hunk({ vim.fn.line("."), vim.fn.line("v") })
        end, { desc = "Stage selected hunk" })

        map("v", "<leader>gR", function()
          gs.reset_hunk({ vim.fn.line("."), vim.fn.line("v") })
        end, { desc = "Reset selected hunk" })

        -- Fugitive shortcut (normal mode)
        map("n", "<leader>gl", "<cmd>Git log<CR>", { desc = "Git log (Fugitive)" })
      end,
    },
  },
}
