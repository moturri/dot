return {
	"nvim-neo-tree/neo-tree.nvim",
	version = "*",
	dependencies = {
		"nvim-lua/plenary.nvim",
		"nvim-tree/nvim-web-devicons",
		"MunifTanjim/nui.nvim",
	},
	config = function()
		require("neo-tree").setup({
			close_if_last_window = true,
			enable_diagnostics = true,
			filesystem = {
				filtered_items = {
					visible = true,
					hide_dotfiles = false,
					-- hide_gitignored = false,
				},
			},

			default_component_configs = {
				name = {
					trailing_slash = true,
					use_git_status_colors = true,
				},
			},
		})
		vim.keymap.set("n", "<C-n>", ":Neotree reveal toggle<CR>", {})
		vim.keymap.set("n", "<leader>bf", ":Neotree buffers reveal float<CR>", {})
	end,
}
