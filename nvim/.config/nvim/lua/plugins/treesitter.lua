return {
	{
		"nvim-treesitter/nvim-treesitter",
		build = ":TSUpdate", -- Automatically update parsers
		version = "*",
		config = function()
			require("nvim-treesitter.configs").setup({
				-- Ensure installed parsers (you can specify specific parsers or "all")
				ensure_installed = { "python", "lua", "javascript", "bash" }, -- Automatically install all available parsers
				sync_install = false, -- Do not install parsers synchronously
				auto_install = true, -- Automatically install missing parsers
				ignore_install = {}, -- Ignore specific parsers (if needed)

				highlight = {
					enable = true, -- Enable syntax highlighting
					additional_vim_regex_highlighting = false, -- Disable Vim's regex-based highlighting
				},

				indent = {
					enable = true, -- Enable indentation based on treesitter
				},

				incremental_selection = {
					enable = true, -- Enable incremental selection
					keymaps = {
						init_selection = "<C-space>", -- Initial selection keybinding
						node_incremental = "<C-space>", -- Incremental node selection
						scope_incremental = "<C-s>", -- Incremental scope selection
						node_decremental = "<C-backspace>", -- Decremental node selection
					},
				},

				autotag = {
					enable = true, -- Enable auto-closing tags (useful for HTML/XML)
				},

				textobjects = {
					select = {
						enable = true, -- Enable textobject selection
						lookahead = true, -- Enable lookahead for better textobject detection
						keymaps = {
							["af"] = "@function.outer", -- Select outer function
							["if"] = "@function.inner", -- Select inner function
							["ac"] = "@class.outer", -- Select outer class
							["ic"] = "@class.inner", -- Select inner class
						},
					},
					move = {
						enable = true, -- Enable textobject movement
						set_jumps = true, -- Enable jump commands for movement
						keymaps = {
							["[f"] = { query = "@function.outer", desc = "Previous function" },
							["]f"] = { query = "@function.outer", desc = "Next function" },
							["[c"] = { query = "@class.outer", desc = "Previous class" },
							["]c"] = { query = "@class.outer", desc = "Next class" },
						},
					},
				},

				context_commentstring = {
					enable = true, -- Enable automatic comment string adjustments
					enable_autocmd = false, -- Disable autocommand for commentstring (optional, can be left as is)
				},

				-- Disable unused modules for performance optimization
				modules = {
					textsubjects = { enable = false }, -- Disable textsubjects if not needed
					rainbow = { enable = false }, -- Disable rainbow parentheses if not needed
				},

				fold = {
					enable = true, -- Enable code folding based on treesitter
					custom_fold = "nvim_treesitter#foldexpr()", -- Custom fold expression
				},
			})
		end,
	},
}
