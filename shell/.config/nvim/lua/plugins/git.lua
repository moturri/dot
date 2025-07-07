return {
	-- Vim Fugitive (Git CLI) — no keymaps, just load on demand
	{
		"tpope/vim-fugitive",
		cmd = { "Git", "G" },
	},

	-- Git signs, but no keymaps to avoid overriding snacks
	{
		"lewis6991/gitsigns.nvim",
		event = { "BufReadPre", "BufNewFile" },
		opts = {
			signs = {
				add = { text = " " },
				change = { text = " " },
				delete = { text = " " },
				topdelete = { text = " " },
				changedelete = { text = "󰐕 " },
				untracked = { text = " " },
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

			-- Disable all default keymaps here
			on_attach = function(bufnr)
				local gs = package.loaded.gitsigns
				-- You can optionally add minimal keymaps here if needed
				-- but keep empty or minimal to avoid overriding snacks
			end,
		},
	},
}
