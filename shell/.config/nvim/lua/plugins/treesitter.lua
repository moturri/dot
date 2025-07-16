return {
	"nvim-treesitter/nvim-treesitter",
	lazy = false,
	build = ":TSUpdate",
	dependencies = {
		"nvim-treesitter/nvim-treesitter-textobjects",
		"windwp/nvim-ts-autotag",
		"JoosepAlviste/nvim-ts-context-commentstring",
		"nvim-treesitter/playground",
	},
	config = function()
		require("nvim-treesitter.configs").setup({
			ensure_installed = {
				"html",
				"css",
				"scss",
				"javascript",
				"typescript",
				"tsx",
				"vue",
				"svelte",
				"json",
				"bash",
				"lua",
				"vim",
				"vimdoc",
				"regex",
				"markdown",
				"markdown_inline",
				"yaml",
				"python",
				"latex",
				"typst",
				"norg",
			},
			auto_install = true,
			ignore_install = { "phpdoc" }, -- optional
			highlight = {
				enable = true,
				disable = function(_, bufnr)
					local max = 100 * 1024
					local ok, stat = pcall(vim.loop.fs_stat, vim.api.nvim_buf_get_name(bufnr))
					return ok and stat and stat.size > max
				end,
			},
			indent = { enable = true },
			incremental_selection = {
				enable = true,
				keymaps = {
					init_selection = "gnn",
					node_incremental = "grn",
					node_decremental = "grm",
				},
			},
			autotag = { enable = true },
			textobjects = {
				select = {
					enable = true,
					lookahead = true,
				},
				move = {
					enable = true,
					set_jumps = true,
					goto_next_start = {
						["]f"] = "@function.outer",
						["]c"] = "@class.outer",
						["]a"] = "@parameter.outer",
					},
					goto_previous_start = {
						["[f"] = "@function.outer",
						["[c"] = "@class.outer",
						["[a"] = "@parameter.outer",
					},
				},
				swap = {
					enable = true,
					swap_next = { ["<leader>sn"] = "@parameter.inner" },
					swap_previous = { ["<leader>sp"] = "@parameter.inner" },
				},
			},
			playground = {
				enable = true,
				disable = {},
				updatetime = 25,
				persist_queries = false,
			},
		})

		require("ts_context_commentstring").setup()
	end,
}
