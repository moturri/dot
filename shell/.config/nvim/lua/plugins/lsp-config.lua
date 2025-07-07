return {
	-- Mason: external tooling manager (LSPs, linters, formatters)
	{
		"williamboman/mason.nvim",
		event = { "BufReadPre", "BufNewFile" },
		opts = {
			ui = { border = "rounded" },
		},
	},

	-- Bridge Mason with lspconfig
	{
		"williamboman/mason-lspconfig.nvim",
		event = { "BufReadPre", "BufNewFile" },
		opts = {
			automatic_installation = true,
		},
	},

	-- Ensure Mason installs the required tools
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
					"tombi",
					"stylua",
					"black",
					"isort",
					"clang-format",
					"shfmt",
					"prettier",
					"flake8",
					"eslint_d",
					"luacheck",
					"shellcheck",
					"jsonlint",
					"pyright",
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

			-- Setup capabilities for completion (nvim-cmp)
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

			-- Disable LSP formatting to avoid conflict with external formatter
			local function on_attach(client, bufnr)
				local map = vim.keymap.set
				local opts = { buffer = bufnr, silent = true, noremap = true }

				client.server_capabilities.documentFormattingProvider = false
				client.server_capabilities.documentRangeFormattingProvider = false

				-- Optional: attach navic winbar if available
				local ok_navic, navic = pcall(require, "nvim-navic")
				if ok_navic and client.server_capabilities.documentSymbolProvider then
					navic.attach(client, bufnr)
				end
			end

			-- Debug: notify when LSP attaches (optional)
			vim.api.nvim_create_autocmd("LspAttach", {
				callback = function(args)
					local client = vim.lsp.get_client_by_id(args.data.client_id)
					vim.notify("LSP attached: " .. client.name, vim.log.levels.INFO)
				end,
			})

			-- Ignore servers here if you want
			local ignore = {
				tombi = true,
			}

			local mason_lspconfig = require("mason-lspconfig")
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

	-- Conform: formatting using external tools configured by Mason
	{
		"stevearc/conform.nvim",
		event = { "BufReadPre", "BufNewFile" },
		config = function()
			local conform = require("conform")

			conform.setup({
				formatters_by_ft = {
					lua = { "stylua" },
					python = { "isort", "black" },
					javascript = { "prettier" },
					typescript = { "prettier" },
					c = { "clang_format" },
					cpp = { "clang_format" },
					sh = { "shfmt" },
					json = { "prettier" },
					yaml = { "prettier" },
					markdown = { "prettier" },
				},
				format_on_save = false,
			})

			vim.keymap.set("n", "<leader>gf", function()
				conform.format({ async = true, lsp_fallback = true })
			end, { desc = "Format buffer" })
		end,
	},

	-- nvim-lint: linting using external linters configured by Mason
	{
		"mfussenegger/nvim-lint",
		config = function()
			local lint = require("lint")

			lint.linters_by_ft = {
				sh = { "shellcheck" },
				python = { "flake8" },
				markdown = { "markdownlint" },
			}

			vim.keymap.set("n", "<leader>ge", vim.diagnostic.open_float, { desc = "Show line diagnostics" })
			vim.keymap.set("n", "<leader>gl", function()
				lint.try_lint()
			end, { desc = "Manually lint current buffer" })
		end,
	},
}
