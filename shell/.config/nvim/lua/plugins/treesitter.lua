---@diagnostic disable: undefined-global

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
		local ok, configs = pcall(require, "nvim-treesitter.configs")
		if not ok then
			vim.notify("nvim-treesitter: failed to load configs", vim.log.levels.ERROR)
			return
		end

		configs.setup({
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
				"norg",
				"typst",
			},
			auto_install = true,
			ignore_install = { "phpdoc" },

			highlight = {
				enable = true,
				disable = function(_, bufnr)
					local max_size = 100 * 1024 -- 100KB
					local stat_ok, stat = pcall(vim.uv.fs_stat, vim.api.nvim_buf_get_name(bufnr))
					return stat_ok and stat and stat.size > max_size
				end,
				additional_vim_regex_highlighting = false,
			},

			indent = { enable = true },

			incremental_selection = {
				enable = true,
				keymaps = {
					init_selection = "gnn",
					node_incremental = "grn",
					node_decremental = "grm",
					scope_incremental = "grc",
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
				updatetime = 50,
				persist_queries = false,
			},
		})

		-- Safe context-commentstring setup
		pcall(function()
			require("ts_context_commentstring").setup({
				enable_autocmd = false,
			})
		end)
	end,
}
