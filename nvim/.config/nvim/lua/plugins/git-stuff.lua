return {
  {
    "tpope/vim-fugitive", -- Git commands in Vim
  },
  {
    "lewis6991/gitsigns.nvim", -- Git signs in the gutter
    version = "*",
    config = function()
      require("gitsigns").setup({
        signs = {
          add = { text = " " }, -- nf-fa-plus
          change = { text = " " }, -- nf-oct-diff
          delete = { text = " " }, -- nf-oct-diff_removed
          topdelete = { text = " " },
          changedelete = { text = "󰐕 " }, -- nf-md-git_compare
          untracked = { text = " " }, -- nf-oct-file_added
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

          local function map(mode, l, r, opts)
            opts = opts or {}
            opts.buffer = bufnr
            vim.keymap.set(mode, l, r, opts)
          end

          -- Navigation
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

          -- Actions
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
