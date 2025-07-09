return {
	"nvim-treesitter/nvim-treesitter",
	event = { "VeryLazy" },

	dependencies = {
		"nvim-treesitter/nvim-treesitter-textobjects",
		"windwp/nvim-ts-autotag",
		"JoosepAlviste/nvim-ts-context-commentstring",
	},

	config = function()
		require("nvim-treesitter.configs").setup({
			ensure_installed = vim.tbl_flatten({
				{ "html", "css", "scss", "javascript", "typescript", "tsx", "vue", "svelte", "json" },
				{ "bash", "lua", "vim", "vimdoc", "regex" },
				{ "markdown", "markdown_inline", "yaml" },
				{ "python" },
				{ "latex", "typst" },
				{ "norg" },
			}),

			sync_install = false,
			auto_install = true,

			highlight = {
				enable = true,
				additional_vim_regex_highlighting = false,
				disable = function(lang, bufnr)
					local max_filesize = 100 * 1024
					local ok, stats = pcall(vim.loop.fs_stat, vim.api.nvim_buf_get_name(bufnr))
					if ok and stats and stats.size > max_filesize then
						return true
					end
				end,
			},

			indent = {
				enable = true,
				-- disable = { "yaml" },
			},

			incremental_selection = {
				enable = true,
				keymaps = {
					init_selection = "<C-space>",
					node_incremental = "<C-space>",
					scope_incremental = "<C-s>",
					node_decremental = "<C-backspace>",
				},
			},

			autotag = {
				enable = true,
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
						["aa"] = "@parameter.outer",
						["ia"] = "@parameter.inner",
						["ai"] = "@conditional.outer",
						["ii"] = "@conditional.inner",
						["al"] = "@loop.outer",
						["il"] = "@loop.inner",
						["ab"] = "@block.outer",
						["ib"] = "@block.inner",
						["as"] = "@statement.outer",
					},
				},
				move = {
					enable = true,
					set_jumps = true,
					goto_next_start = {
						["]f"] = "@function.outer",
						["]c"] = "@class.outer",
						["]a"] = "@parameter.outer",
						["]i"] = "@conditional.outer",
						["]l"] = "@loop.outer",
						["]b"] = "@block.outer",
						["]s"] = "@statement.outer",
					},
					goto_previous_start = {
						["[f"] = "@function.outer",
						["[c"] = "@class.outer",
						["[a"] = "@parameter.outer",
						["[i]"] = "@conditional.outer",
						["[l"] = "@loop.outer",
						["[b"] = "@block.outer",
						["[s"] = "@statement.outer",
					},
				},
				swap = {
					enable = true,
					swap_next = {
						["<leader>sn"] = "@parameter.inner",
					},
					swap_previous = {
						["<leader>sp"] = "@parameter.inner",
					},
				},
			},
		})

		require("ts_context_commentstring").setup()
	end,
}

