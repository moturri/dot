return {
	-- Mason: LSP/DAP/linter installer
	{
		"williamboman/mason.nvim",
		lazy = false,
		config = function()
			require("mason").setup()

			-- Optional: fidget for LSP status notifications
			local fidget_ok, fidget = pcall(require, "fidget")
			if fidget_ok then
				fidget.setup({})
			end
		end,
	},

	-- Mason bridge to lspconfig
	{
		"williamboman/mason-lspconfig.nvim",
		lazy = false,
		opts = {
			automatic_installation = true,
		},
	},

	-- LSP config
	{
		"neovim/nvim-lspconfig",
		lazy = false,
		config = function()
			local lspconfig = require("lspconfig")
			local mason_lspconfig = require("mason-lspconfig")

			-- Capabilities (with fallback)
			local has_cmp, cmp_nvim_lsp = pcall(require, "cmp_nvim_lsp")
			local capabilities = has_cmp and cmp_nvim_lsp.default_capabilities()
				or vim.lsp.protocol.make_client_capabilities()

			-- LSP on_attach
			local function on_attach(client, bufnr)
				local keymap = vim.keymap.set
				local opts = { noremap = true, silent = true, buffer = bufnr }

				keymap("n", "K", vim.lsp.buf.hover, opts)
				keymap("n", "<leader>gd", vim.lsp.buf.definition, opts)
				keymap("n", "<leader>gr", vim.lsp.buf.references, opts)
				keymap("n", "<leader>ca", vim.lsp.buf.code_action, opts)
				keymap("n", "<leader>rn", vim.lsp.buf.rename, opts)
				keymap("n", "<leader>f", function()
					vim.lsp.buf.format({ async = true })
				end, opts)

				-- Optional: Attach navic
				local navic_ok, navic = pcall(require, "nvim-navic")
				if navic_ok and client.server_capabilities.documentSymbolProvider then
					navic.attach(client, bufnr)
				end
			end

			-- Modern diagnostics config (no deprecated sign_define)
			vim.diagnostic.config({
				virtual_text = true,
				signs = {
					text = {
						[vim.diagnostic.severity.ERROR] = "",
						[vim.diagnostic.severity.WARN] = "",
						[vim.diagnostic.severity.HINT] = "",
						[vim.diagnostic.severity.INFO] = "",
					},
				},
				underline = true,
				update_in_insert = false,
				severity_sort = true,
			})

			local default_config = {
				on_attach = on_attach,
				capabilities = capabilities,
			}

			-- Setup all LSPs via mason
			mason_lspconfig.setup_handlers({
				function(server_name)
					lspconfig[server_name].setup(default_config)
				end,
			})
		end,
	},

	-- Completion engine
	{
		"hrsh7th/nvim-cmp",
		version = "*",
		dependencies = {
			"hrsh7th/cmp-nvim-lsp",
			version = "*",
			"L3MON4D3/LuaSnip",
			version = "*",
			"saadparwaiz1/cmp_luasnip",
			version = "*",
			"rafamadriz/friendly-snippets",
			version = "*",
		},
		config = function()
			local cmp = require("cmp")
			local luasnip = require("luasnip")

			cmp.setup({
				snippet = {
					expand = function(args)
						luasnip.lsp_expand(args.body)
					end,
				},
				mapping = cmp.mapping.preset.insert({
					["<C-Space>"] = cmp.mapping.complete(),
					["<C-e>"] = cmp.mapping.abort(),
					["<CR>"] = cmp.mapping.confirm({ select = true }),
					["<C-b>"] = cmp.mapping.scroll_docs(-4),
					["<C-f>"] = cmp.mapping.scroll_docs(4),
				}),
				sources = {
					{ name = "nvim_lsp" },
					{ name = "luasnip" },
					{ name = "buffer" },
				},
				window = {
					completion = cmp.config.window.bordered(),
					documentation = cmp.config.window.bordered(),
				},
			})
		end,
	},

	-- LuaSnip setup with safe loader
	{
		"L3MON4D3/LuaSnip",
		version = "*",
		dependencies = {
			"saadparwaiz1/cmp_luasnip",
			"rafamadriz/friendly-snippets",
		},
		config = function()
			local loader = require("luasnip.loaders.from_vscode")
			if loader.lazy_load then
				loader.lazy_load()
			elseif loader.load then
				loader.load()
			end
		end,
	},

	-- CMP source for LSP
	{
		"hrsh7th/cmp-nvim-lsp",
	},
}
