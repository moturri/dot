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
          add = { text = "▎" },
          change = { text = "▎" },
          delete = { text = "契" },
          topdelete = { text = "契" },
          changedelete = { text = "▎" },
          untracked = { text = "▎" },
        },
        preview_config = {
          border = "rounded",   -- Rounded border for preview
        },
        current_line_blame = false, -- Disable current line blame
        current_line_blame_opts = {
          virt_text = true,     -- Use virtual text for blame
          virt_text_pos = "eol", -- Position of virtual text
          delay = 500,          -- Delay for displaying blame
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
            if vim.wo.diff then return "]c" end
            vim.schedule(function() gs.next_hunk() end)
            return "<Ignore>"
          end, { expr = true })

          map("n", "[c", function()
            if vim.wo.diff then return "[c" end
            vim.schedule(function() gs.prev_hunk() end)
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
