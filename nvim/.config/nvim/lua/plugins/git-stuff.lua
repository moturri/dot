return {
  {
    "tpope/vim-fugitive", -- Git commands in Vim
  },
  {
    "lewis6991/gitsigns.nvim", -- Git signs in the gutter
    config = function()
      require("gitsigns").setup({
        preview_config = {
          border = "rounded",   -- Rounded border for preview
        },
        current_line_blame = false, -- Disable current line blame
        current_line_blame_opts = {
          virt_text = true,     -- Use virtual text for blame
          virt_text_pos = "eol", -- Position of virtual text
          delay = 500,          -- Delay for displaying blame
        },
      })

      -- Key mappings for Gitsigns
      local keymap = vim.keymap.set
      local opts = { noremap = true, silent = true }

      keymap("n", "<leader>gp", ":Gitsigns preview_hunk<CR>", opts)
      keymap("n", "<leader>gt", ":Gitsigns toggle_current_line_blame<CR>", opts)
      keymap("n", "<leader>ga", ":Gitsigns stage_hunk<CR>", opts)
      keymap("n", "<leader>gs", ":Gitsigns undo_stage_hunk<CR>", opts)
      keymap("n", "<leader>gq", ":Gitsigns diffthis<CR>", opts)
      keymap("n", "<leader>gR", ":Gitsigns reset_hunk<CR>", opts)
      keymap("n", "<leader>gl", ":Git log<CR>", opts)
    end,
  },
}
