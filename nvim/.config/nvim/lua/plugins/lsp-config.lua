return {
	-- Mason Setup
	{
		"williamboman/mason.nvim",
		event = { "BufReadPre", "BufNewFile" },
		config = function()
			require("mason").setup({
				ui = { border = "rounded" },
			})
		end,
	},

	-- Mason-LSPConfig Setup
	{
		"williamboman/mason-lspconfig.nvim",
		event = { "BufReadPre", "BufNewFile" },
		opts = {
			automatic_installation = true,
		},
	},

	-- LSPConfig Setup
	{
		"neovim/nvim-lspconfig",
		event = { "BufReadPre", "BufNewFile" },
		config = function()
			local lspconfig = require("lspconfig")

			-- Capabilities for completion (nvim-cmp)
			local capabilities = vim.lsp.protocol.make_client_capabilities()
			local ok_cmp, cmp_nvim_lsp = pcall(require, "cmp_nvim_lsp")
			if ok_cmp then
				capabilities = cmp_nvim_lsp.default_capabilities(capabilities)
			end

			-- Diagnostic signs
			vim.diagnostic.config({
				signs = {
					text = {
						[vim.diagnostic.severity.ERROR] = "",
						[vim.diagnostic.severity.WARN] = "",
						[vim.diagnostic.severity.HINT] = "",
						[vim.diagnostic.severity.INFO] = "",
					},
				},
				virtual_text = true,
				underline = true,
				update_in_insert = false,
				severity_sort = true,
				float = { border = "rounded" },
			})

			-- Common on_attach function
			local function on_attach(client, bufnr)
				local map = vim.keymap.set
				local opts = { noremap = true, silent = true, buffer = bufnr }

				map("n", "K", vim.lsp.buf.hover, opts)
				map("n", "<leader>gd", vim.lsp.buf.definition, opts)
				map("n", "<leader>gr", vim.lsp.buf.references, opts)
				map("n", "<leader>ca", vim.lsp.buf.code_action, opts)
				map("n", "<leader>rn", vim.lsp.buf.rename, opts)
				map("n", "<leader>f", function()
					vim.lsp.buf.format({ async = true })
				end, opts)

				-- Attach navic if available
				local ok_navic, navic = pcall(require, "nvim-navic")
				if ok_navic and client.server_capabilities.documentSymbolProvider then
					navic.attach(client, bufnr)
				end
			end

			-- Setup servers automatically via mason-lspconfig
			local mason_lspconfig = require("mason-lspconfig")
			for _, server in ipairs(mason_lspconfig.get_installed_servers()) do
				lspconfig[server].setup({
					capabilities = capabilities,
					on_attach = on_attach,
				})
			end
		end,
	},
}
