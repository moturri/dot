return {
	{
		"tpope/vim-fugitive",
	},
	{
		"lewis6991/gitsigns.nvim",
		config = function()
			require("gitsigns").setup({
				preview_config = {
					border = "rounded",
				},
				current_line_blame = false,
				current_line_blame_opts = {
					virt_text = true,
					virt_text_pos = "eol",
					delay = 500,
				},
			})

			vim.keymap.set("n", "<leader>gp", ":Gitsigns preview_hunk<CR>", { noremap = true, silent = true })
			vim.keymap.set(
				"n",
				"<leader>gt",
				":Gitsigns toggle_current_line_blame<CR>",
				{ noremap = true, silent = true }
			)
			vim.keymap.set("n", "<leader>ga", ":Gitsigns stage_hunk<CR>", { noremap = true, silent = true })
			vim.keymap.set("n", "<leader>gs", ":Gitsigns undo_stage_hunk<CR>", { noremap = true, silent = true })
			vim.keymap.set("n", "<leader>gq", ":Gitsigns diffthis<CR>", { noremap = true, silent = true })
			vim.keymap.set("n", "<leader>gR", ":Gitsigns reset_hunk<CR>", { noremap = true, silent = true })
			vim.keymap.set("n", "<leader>gl", ":Git log<CR>", { noremap = true, silent = true })
		end,
	},
}
