return {
	{
		"williamboman/mason.nvim",
		lazy = false,
		config = function()
			require("mason").setup()
			require("fidget").setup({})
		end,
	},

	{
		"williamboman/mason-lspconfig.nvim",
		lazy = false,
		opts = {
			automatic_installation = true,
		},
	},

	{
		"neovim/nvim-lspconfig",
		lazy = false,
		config = function()
			local lspconfig = require("lspconfig")
			local mason_lspconfig = require("mason-lspconfig")
			local capabilities = require("cmp_nvim_lsp").default_capabilities()

			local function on_attach(client, bufnr)
				local opts = { noremap = true, silent = true, buffer = bufnr }
				local keymap = vim.keymap.set

				keymap("n", "K", vim.lsp.buf.hover, opts)
				keymap("n", "<leader>gd", vim.lsp.buf.definition, opts)
				keymap("n", "<leader>gr", vim.lsp.buf.references, opts)
				keymap("n", "<leader>ca", vim.lsp.buf.code_action, opts)
				keymap("n", "<leader>rn", vim.lsp.buf.rename, opts)
				keymap("n", "<leader>f", function()
					vim.lsp.buf.format({ async = true })
				end, opts)

				local navic_ok, navic = pcall(require, "nvim-navic")
				if navic_ok and client.server_capabilities.documentSymbolProvider then
					navic.attach(client, bufnr)
				end
			end

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
}
