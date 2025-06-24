return {
	-- Mason: package manager for LSP/DAP/formatters
	{
		"williamboman/mason.nvim",
		event = { "BufReadPre", "BufNewFile" },
		config = function()
			require("mason").setup({
				ui = { border = "rounded" },
			})
		end,
	},

	-- Mason bridge for LSPConfig
	{
		"williamboman/mason-lspconfig.nvim",
		event = { "BufReadPre", "BufNewFile" },
		opts = {
			automatic_installation = true,
		},
	},

	-- Neovim's built-in LSP setup
	{
		"neovim/nvim-lspconfig",
		event = { "BufReadPre", "BufNewFile" },
		config = function()
			local lspconfig = require("lspconfig")

			-- Add nvim-cmp completion capabilities
			local capabilities = vim.lsp.protocol.make_client_capabilities()
			local ok_cmp, cmp_lsp = pcall(require, "cmp_nvim_lsp")
			if ok_cmp then
				capabilities = cmp_lsp.default_capabilities(capabilities)
			end

			-- Diagnostic signs (KISS + symbols)
			local signs = {
				Error = "",
				Warn = "",
				Hint = "",
				Info = "",
			}
			for type, icon in pairs(signs) do
				local hl = "DiagnosticSign" .. type
				vim.fn.sign_define(hl, { text = icon, texthl = hl, numhl = hl })
			end

			vim.diagnostic.config({
				virtual_text = true,
				underline = true,
				severity_sort = true,
				float = { border = "rounded" },
				update_in_insert = false,
			})

			-- Common on_attach (buffer-local keymaps)
			local function on_attach(client, bufnr)
				local map = vim.keymap.set
				local opts = { buffer = bufnr, silent = true, noremap = true }

				map("n", "K", vim.lsp.buf.hover, opts)
				map("n", "<leader>gd", vim.lsp.buf.definition, opts)
				map("n", "<leader>gr", vim.lsp.buf.references, opts)
				map("n", "<leader>ca", vim.lsp.buf.code_action, opts)
				map("n", "<leader>rn", vim.lsp.buf.rename, opts)
				map("n", "<leader>f", function()
					vim.lsp.buf.format({ async = true })
				end, opts)

				-- Optional: navic integration
				local ok_navic, navic = pcall(require, "nvim-navic")
				if ok_navic and client.server_capabilities.documentSymbolProvider then
					navic.attach(client, bufnr)
				end
			end

			-- Setup servers from Mason
			local ok_mason, mason_lspconfig = pcall(require, "mason-lspconfig")
			if not ok_mason then
				return
			end

			for _, server in ipairs(mason_lspconfig.get_installed_servers() or {}) do
				lspconfig[server].setup({
					capabilities = capabilities,
					on_attach = on_attach,
				})
			end
		end,
	},
}
