return {
  -- Git CLI Wrapper: Fugitive
  {
    "tpope/vim-fugitive",
    cmd = { "Git", "G" }, -- Lazy-load on Git command usage
  },

  -- Git Signs: visual indicators + hunk actions
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
        style = "minimal",
        relative = "cursor",
        row = 0,
        col = 1,
      },
      current_line_blame = false,
      current_line_blame_opts = {
        virt_text = true,
        virt_text_pos = "eol",
        delay = 500,
      },
      attach_to_untracked = true,
      word_diff = false,
      max_file_length = 40000,
      update_debounce = 100,

      on_attach = function(bufnr)
        local gs = package.loaded.gitsigns
        local function map(mode, lhs, rhs, desc)
          vim.keymap.set(mode, lhs, rhs, { buffer = bufnr, desc = desc })
        end

        -- Hunk navigation
        map("n", "]c", function()
          if vim.wo.diff then return "]c" end
          vim.schedule(gs.next_hunk)
          return "<Ignore>"
        end, "Next hunk")

        map("n", "[c", function()
          if vim.wo.diff then return "[c" end
          vim.schedule(gs.prev_hunk)
          return "<Ignore>"
        end, "Previous hunk")

        -- Git actions
        map("n", "<leader>gp", gs.preview_hunk, "Preview hunk")
        map("n", "<leader>ga", gs.stage_hunk, "Stage hunk")
        map("n", "<leader>gR", gs.reset_hunk, "Reset hunk")
        map("n", "<leader>gs", gs.undo_stage_hunk, "Undo stage")
        map("n", "<leader>gq", gs.diffthis, "Diff buffer")
        map("n", "<leader>gB", gs.toggle_deleted, "Toggle deleted")
        map("n", "<leader>gt", gs.toggle_current_line_blame, "Toggle blame")

        -- Visual mode hunk actions
        map("v", "<leader>ga", function()
          gs.stage_hunk({ vim.fn.line("."), vim.fn.line("v") })
        end, "Stage selection")

        map("v", "<leader>gR", function()
          gs.reset_hunk({ vim.fn.line("."), vim.fn.line("v") })
        end, "Reset selection")

        -- Git log via Fugitive
        map("n", "<leader>gl", "<cmd>Git log<CR>", "Git log (Fugitive)")
      end,
    },
  },
}
