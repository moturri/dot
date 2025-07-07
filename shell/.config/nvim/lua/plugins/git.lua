return {
	-- Git CLI wrapper
	{
		"tpope/vim-fugitive",
		cmd = { "Git", "G" },
	},

	-- Git signs & inline actions
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

			on_attach = function(bufnr)
				local gs = package.loaded.gitsigns
				local map = function(mode, lhs, rhs, desc)
					vim.keymap.set(mode, lhs, rhs, { buffer = bufnr, desc = desc })
				end

				-- Hunk navigation
				map("n", "]c", function()
					if vim.wo.diff then
						return "]c"
					end
					vim.schedule(gs.next_hunk)
					return "<Ignore>"
				end, "Next hunk")

				map("n", "[c", function()
					if vim.wo.diff then
						return "[c"
					end
					vim.schedule(gs.prev_hunk)
					return "<Ignore>"
				end, "Prev hunk")

				-- Hunk actions
				map("n", "<leader>gp", gs.preview_hunk, "Preview hunk")
				map("n", "<leader>ga", gs.stage_hunk, "Stage hunk")
				map("n", "<leader>gr", gs.reset_hunk, "Reset hunk")
				map("n", "<leader>gu", gs.undo_stage_hunk, "Undo stage")
				map("n", "<leader>gd", gs.diffthis, "Diff buffer")
				map("n", "<leader>gD", gs.toggle_deleted, "Toggle deleted")
				map("n", "<leader>gB", gs.toggle_current_line_blame, "Toggle blame")

				-- Visual mode hunk actions
				map("v", "<leader>ga", function()
					local s = vim.fn.line("v")
					local e = vim.fn.line(".")
					gs.stage_hunk({ math.min(s, e), math.max(s, e) })
				end, "Stage selection")

				map("v", "<leader>gr", function()
					local s = vim.fn.line("v")
					local e = vim.fn.line(".")
					gs.reset_hunk({ math.min(s, e), math.max(s, e) })
				end, "Reset selection")

				-- Git log (via Fugitive)
				map("n", "<leader>gl", function()
					vim.cmd("Git log")
				end, "Git log")
			end,
		},
	},
}
