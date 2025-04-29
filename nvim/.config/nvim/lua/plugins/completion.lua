return {
	{
		"hrsh7th/cmp-nvim-lsp", -- LSP source for nvim-cmp
	},
	{
		"L3MON4D3/LuaSnip", -- Snippet engine
		dependencies = {
			"saadparwaiz1/cmp_luasnip", -- Source for LuaSnip
			"rafamadriz/friendly-snippets", -- Predefined snippets
		},
		config = function()
			require("luasnip.loaders.from_vscode").lazy_load()
		end,
	},
	{
		"hrsh7th/nvim-cmp", -- Main completion plugin
		version = "*",
		dependencies = {
			"hrsh7th/cmp-nvim-lsp",
			"L3MON4D3/LuaSnip",
			"saadparwaiz1/cmp_luasnip",
			"rafamadriz/friendly-snippets",
		},
		config = function()
			local cmp = require("cmp")
			local luasnip = require("luasnip")

			cmp.setup({
				snippet = {
					expand = function(args)
						luasnip.lsp_expand(args.body) -- Expand snippets
					end,
				},
				mapping = cmp.mapping.preset.insert({
					["<C-Space>"] = cmp.mapping.complete(), -- Trigger completion
					["<C-e>"] = cmp.mapping.abort(), -- Abort completion
					["<CR>"] = cmp.mapping.confirm({ select = true }), -- Confirm selection
					["<C-b>"] = cmp.mapping.scroll_docs(-4), -- Scroll documentation up
					["<C-f>"] = cmp.mapping.scroll_docs(4), -- Scroll documentation down
				}),
				sources = {
					{ name = "nvim_lsp" }, -- LSP source
					{ name = "luasnip" }, -- Snippet source
					{ name = "buffer" }, -- Buffer source
				},
				window = {
					completion = cmp.config.window.bordered(), -- Bordered completion window
					documentation = cmp.config.window.bordered(), -- Bordered documentation window
				},
			})
		end,
	},
}
