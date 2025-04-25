return {
	{
		"williamboman/mason.nvim",
		lazy = false,
		config = function()
			require("fidget").setup({})
			require("mason").setup()
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

			-- -- Optional: enhance capabilities for folding, etc.
			-- capabilities.textDocument.foldingRange = {
			-- 	dynamicRegistration = false,
			-- 	lineFoldingOnly = true,
			-- }

			-- Attach function with navic + keymaps
			local function on_attach(client, bufnr)
				local keymap = vim.keymap.set
				local opts = { noremap = true, silent = true, buffer = bufnr }

				-- LSP Keymaps
				keymap("n", "K", vim.lsp.buf.hover, opts)
				keymap("n", "<leader>gd", vim.lsp.buf.definition, opts)
				keymap("n", "<leader>gr", vim.lsp.buf.references, opts)
				keymap("n", "<leader>ca", vim.lsp.buf.code_action, opts)
				keymap("n", "<leader>rn", vim.lsp.buf.rename, opts)
				keymap("n", "<leader>f", function()
					vim.lsp.buf.format({ async = true })
				end, opts)

				-- Attach nvim-navic if available
				local navic_ok, navic = pcall(require, "nvim-navic")
				if navic_ok and client.server_capabilities.documentSymbolProvider then
					navic.attach(client, bufnr)
				end
			end

			-- Default LSP config
			local default_config = {
				on_attach = on_attach,
				capabilities = capabilities,
			}

			-- Setup all servers, and customize as needed
			mason_lspconfig.setup_handlers({
				-- Default setup for all servers
				function(server_name)
					lspconfig[server_name].setup(default_config)
				end,
			})
		end,
	},
}
