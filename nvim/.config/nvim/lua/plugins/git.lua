return {
  -- Fugitive for advanced Git interaction
  {
    "tpope/vim-fugitive",
    cmd = { "Git", "G" }, -- Lazy load on command use
  },

  -- Gitsigns for inline git changes
  {
    "lewis6991/gitsigns.nvim",
    event = { "BufReadPre", "BufNewFile" },
    opts = {
      signs = {
        add          = { text = " " },
        change       = { text = " " },
        delete       = { text = " " },
        topdelete    = { text = " " },
        changedelete = { text = "󰐕 " },
        untracked    = { text = " " },
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
      on_attach = function(bufnr)
        local gs = package.loaded.gitsigns
        local map = function(mode, lhs, rhs, opts)
          opts = vim.tbl_extend("force", { buffer = bufnr }, opts or {})
          vim.keymap.set(mode, lhs, rhs, opts)
        end

        -- Navigation
        map("n", "]c", function()
          if vim.wo.diff then return "]c" end
          vim.schedule(gs.next_hunk)
          return "<Ignore>"
        end, { expr = true, desc = "Next Git hunk" })

        map("n", "[c", function()
          if vim.wo.diff then return "[c" end
          vim.schedule(gs.prev_hunk)
          return "<Ignore>"
        end, { expr = true, desc = "Previous Git hunk" })

        -- Git actions
        map("n", "<leader>gp", gs.preview_hunk, { desc = "Preview hunk" })
        map("n", "<leader>gt", gs.toggle_current_line_blame, { desc = "Toggle blame" })
        map("n", "<leader>ga", gs.stage_hunk, { desc = "Stage hunk" })
        map("n", "<leader>gs", gs.undo_stage_hunk, { desc = "Undo stage hunk" })
        map("n", "<leader>gq", gs.diffthis, { desc = "Diff current buffer" })
        map("n", "<leader>gR", gs.reset_hunk, { desc = "Reset hunk" })
        map("n", "<leader>gB", gs.toggle_deleted, { desc = "Toggle deleted lines" })

        -- Visual mode: stage/reset selected lines
        map("v", "<leader>ga", function()
          gs.stage_hunk({ vim.fn.line("."), vim.fn.line("v") })
        end, { desc = "Stage selected hunk" })

        map("v", "<leader>gR", function()
          gs.reset_hunk({ vim.fn.line("."), vim.fn.line("v") })
        end, { desc = "Reset selected hunk" })

        -- Fugitive Git log
        map("n", "<leader>gl", "<cmd>Git log<CR>", { desc = "Git log (Fugitive)" })
      end,
    },
  },
}
