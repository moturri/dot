return {
	{
		"nvim-treesitter/nvim-treesitter",
		build = ":TSUpdate",
		config = function()
			require("nvim-treesitter.configs").setup({
				ensure_installed = {
					"c",
					"lua",
					"cpp",
					"bash",
					"javascript",
					"python",
					"typescript",
					"html",
					"gitignore",
					"vue",
					"rust",
					"markdown",
					"markdown_inline",
					"json",
					"sql",
					"css",
					"yaml",
					"toml",
					"terraform",
				},
				sync_install = false,
				ignore_install = {},
				auto_install = true, -- Automatically install missing parsers

				highlight = {
					enable = true, -- Enable highlighting
					additional_vim_regex_highlighting = false,
				},
				indent = {
					enable = true, -- Enable tree-sitter based indentation
				},
				incremental_selection = {
					enable = true,
					keymaps = {
						init_selection = "<c-space>",
						node_incremental = "<c-space>",
						scope_incremental = "<c-s>",
						node_decremental = "<c-backspace>",
					},
				},
				autotag = {
					enable = true, -- Enable autotagging for HTML, XML, etc.
				},
				textobjects = {
					select = {
						enable = true,
						lookahead = true,
						keymaps = {
							["af"] = "@function.outer",
							["if"] = "@function.inner",
							["ac"] = "@class.outer",
							["ic"] = "@class.inner",
						},
					},
				},
				context_commentstring = {
					enable = true, -- Enable integration with 'JoosepAlviste/nvim-ts-context-commentstring'
				},
			})
		end,
	},
}
