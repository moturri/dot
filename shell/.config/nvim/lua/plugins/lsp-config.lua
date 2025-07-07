return {
	-- Mason: installs LSPs, DAPs, formatters
	{
		"williamboman/mason.nvim",
		event = { "BufReadPre", "BufNewFile" },
		opts = {
			ui = { border = "rounded" },
		},
	},

	-- Bridge between Mason and lspconfig
	{
		"williamboman/mason-lspconfig.nvim",
		event = { "BufReadPre", "BufNewFile" },
		opts = {
			automatic_installation = true,
		},
	},

	-- Mason Tool Installer: ensures LSPs, formatters, linters are installed
	{
		"WhoIsSethDaniel/mason-tool-installer.nvim",
		dependencies = { "williamboman/mason.nvim" },
		config = function()
			require("mason-tool-installer").setup({
				ensure_installed = {
					"clangd",
					"marksman",
					"markdownlint",
					"glow",
					"cbfmt",
					"black",
					"tombi",
					"stylua",
					"isort",
					"clang-format",
					"shfmt",
					"prettier",
					"flake8",
					"eslint_d",
					"luacheck",
					"shellcheck",
					"jsonlint",
				},
			})
		end,
	},

	-- LSP configuration
	{
		"neovim/nvim-lspconfig",
		event = { "BufReadPre", "BufNewFile" },
		config = function()
			local vim = vim
			local lspconfig = require("lspconfig")

			-- Add capabilities for nvim-cmp if available
			local capabilities = vim.lsp.protocol.make_client_capabilities()
			local ok_cmp, cmp_lsp = pcall(require, "cmp_nvim_lsp")
			if ok_cmp then
				capabilities = cmp_lsp.default_capabilities(capabilities)
			end

			-- Global diagnostics config
			vim.diagnostic.config({
				virtual_text = true,
				underline = true,
				severity_sort = true,
				update_in_insert = false,
				float = { border = "rounded" },
				signs = {
					text = {
						[vim.diagnostic.severity.ERROR] = "",
						[vim.diagnostic.severity.WARN] = "",
						[vim.diagnostic.severity.HINT] = "",
						[vim.diagnostic.severity.INFO] = "",
					},
				},
			})

			-- Function to run when LSP attaches to a buffer
			local function on_attach(client, bufnr)
				local map = vim.keymap.set
				local opts = { buffer = bufnr, silent = true, noremap = true }

				-- Disable format on save
				client.server_capabilities.documentFormattingProvider = false
				client.server_capabilities.documentRangeFormattingProvider = false

				map("n", "K", vim.lsp.buf.hover, opts)
				map("n", "<leader>gd", vim.lsp.buf.definition, opts)
				map("n", "<leader>gr", vim.lsp.buf.references, opts)
				map("n", "<leader>ca", vim.lsp.buf.code_action, opts)
				map("n", "<leader>rn", vim.lsp.buf.rename, opts)

				-- Optional: navic for winbar context
				local ok_navic, navic = pcall(require, "nvim-navic")
				if ok_navic and client.server_capabilities.documentSymbolProvider then
					navic.attach(client, bufnr)
				end
			end

			-- Debug: log attached LSP client (used by Fidget)
			vim.api.nvim_create_autocmd("LspAttach", {
				callback = function(args)
					local client = vim.lsp.get_client_by_id(args.data.client_id)
					vim.notify("LSP attached: " .. client.name, vim.log.levels.INFO)
				end,
			})

			-- Optional: ignore specific servers from setup
			local ignore = {
				tombi = true,
			}

			-- Setup all installed LSP servers via mason-lspconfig
			local ok_mason, mason_lspconfig = pcall(require, "mason-lspconfig")
			if not ok_mason then
				return
			end

			for _, server in ipairs(mason_lspconfig.get_installed_servers()) do
				if not ignore[server] then
					local ok, server_module = pcall(function()
						return lspconfig[server]
					end)
					if ok and server_module then
						server_module.setup({
							capabilities = capabilities,
							on_attach = on_attach,
						})
					end
				end
			end
		end,
	},
}
