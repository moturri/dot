return {
	{
		"williamboman/mason.nvim",
		version = "*",
		lazy = false,
		config = function()
			require("mason").setup()
		end,
	},

	{
		"williamboman/mason-lspconfig.nvim",
		version = "*",
		lazy = false,
		opts = {
			automatic_installation = true,
		},
	},

	{
		"neovim/nvim-lspconfig",
		version = "*",
		lazy = false,
		config = function()
			local lspconfig = require("lspconfig")
			local mason_lspconfig = require("mason-lspconfig")

			-- Capabilities
			local has_cmp, cmp_nvim_lsp = pcall(require, "cmp_nvim_lsp")
			local capabilities = has_cmp and cmp_nvim_lsp.default_capabilities()
				or vim.lsp.protocol.make_client_capabilities()

			-- LSP on_attach
			local function on_attach(_, bufnr)
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
			end

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

			mason_lspconfig.setup_handlers({
				function(server_name)
					lspconfig[server_name].setup(default_config)
				end,
			})
		end,
	},

	{
		"hrsh7th/nvim-cmp",
		version = "*",
		dependencies = {
			"hrsh7th/cmp-nvim-lsp",
			"L3MON4D3/LuaSnip",
			"saadparwaiz1/cmp_luasnip",
			"rafamadriz/friendly-snippets",
			version = "*",
		},
		config = function()
			local cmp = require("cmp")
			local luasnip = require("luasnip")

			require("luasnip.loaders.from_vscode").lazy_load()

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

	{
		"L3MON4D3/LuaSnip",
		dependencies = {
			"saadparwaiz1/cmp_luasnip",
			"rafamadriz/friendly-snippets",
		},
		config = function() end,
	},
}
